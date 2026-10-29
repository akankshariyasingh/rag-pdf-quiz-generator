
import streamlit as st

from config import (
    GEMINI_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_TOP_K,
)
from pdf_processor import process_pdf
from vector_store import (
    add_chunks,
    list_stored_pdfs,
    get_collection_stats,
    get_stored_chunks,
    retrieve_relevant_chunks,
)
from quiz_generator import generate_quiz
from quiz_evaluator import evaluate_quiz, get_performance_message


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="RAG PDF Quiz Generator",
    page_icon="📚",
    layout="wide",
)

st.title("📚 RAG PDF Quiz Generator")
st.write(
    "Upload a PDF, retrieve relevant document content, "
    "generate a quiz using Gemini, and evaluate your answers."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "quiz_questions": [],
    "quiz_submitted": False,
    "quiz_result": None,
    "quiz_source": None,
    "quiz_difficulty": "Mixed",
    "processed_source": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_quiz():
    st.session_state.quiz_questions = []
    st.session_state.quiz_submitted = False
    st.session_state.quiz_result = None
    st.session_state.quiz_source = None
    st.session_state.quiz_difficulty = "Mixed"


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("⚙️ Configuration")

    st.write(f"**Chunk size:** {CHUNK_SIZE} characters")
    st.write(f"**Chunk overlap:** {CHUNK_OVERLAP} characters")
    st.write("**Vector database:** ChromaDB")
    st.write("**Storage:** Local persistent folder")
    st.code("chroma_db/")
    st.write(f"**Gemini model:** {GEMINI_MODEL}")
    st.caption(
        "ChromaDB retrieves document chunks. "
        "Gemini generates the questions."
    )


# --------------------------------------------------
# DATABASE STATISTICS
# --------------------------------------------------

stats = get_collection_stats()

col1, col2, col3 = st.columns(3)

col1.metric("Stored Chunks", stats["total_chunks"])
col2.metric("Stored PDFs", stats["total_pdfs"])
col3.metric("Chunk Size", CHUNK_SIZE)


# --------------------------------------------------
# 1. UPLOAD AND PROCESS PDF
# --------------------------------------------------

st.header("1. Upload PDF Documents")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a text-based PDF to build your knowledge base.",
)

if uploaded_file is not None:
    st.info(
        f"Selected: {uploaded_file.name} "
        f"({uploaded_file.size / 1024:.2f} KB)"
    )

    if st.button("📄 Process PDF", type="primary"):
        reset_quiz()

        try:
            pdf_bytes = uploaded_file.getvalue()

            if not pdf_bytes:
                st.error("The uploaded PDF is empty.")

            elif not pdf_bytes.startswith(b"%PDF-"):
                st.error("The selected file does not appear to be a valid PDF.")

            else:
                progress = st.progress(0)
                status = st.status(
                    "Processing your PDF...",
                    expanded=True,
                )

                status.write("Reading PDF pages...")
                progress.progress(15)

                status.write("Extracting text and creating chunks...")
                chunks = process_pdf(
                    pdf_bytes,
                    uploaded_file.name,
                )
                progress.progress(65)

                status.write("Saving chunks to ChromaDB...")
                added_count = add_chunks(chunks)
                progress.progress(100)

                status.update(
                    label="PDF processing completed!",
                    state="complete",
                    expanded=False,
                )

                st.session_state.processed_source = uploaded_file.name

                st.success(
                    f"PDF processed successfully! "
                    f"{len(chunks)} chunks created; "
                    f"{added_count} chunks saved or updated."
                )

                st.rerun()

        except Exception as exc:
            st.error(f"PDF processing failed: {exc}")


# --------------------------------------------------
# 2. EXPLORE STORED CHUNKS
# --------------------------------------------------

st.header("2. Explore Stored Document Chunks")

stored_chunks = get_stored_chunks(limit=5)

if stored_chunks:
    st.caption("Showing up to 5 stored chunks.")

    for index, chunk in enumerate(stored_chunks, start=1):
        with st.expander(
            f"Chunk {index} | {chunk['source']} | "
            f"Page {chunk['page_number']}"
        ):
            st.write(chunk["text"])
else:
    st.info("Upload and process a PDF to see its chunks here.")


# --------------------------------------------------
# 3. GENERATE QUIZ
# --------------------------------------------------

st.header("3. AI-Based Question Generation")

stored_pdfs = list_stored_pdfs()
pdf_names = [item["source"] for item in stored_pdfs]

if not pdf_names:
    st.info("Please upload and process a PDF before generating a quiz.")

else:
    selected_pdf = st.selectbox(
        "Select a processed PDF",
        options=pdf_names,
    )

    difficulty = st.selectbox(
        "Choose question difficulty",
        options=["Easy", "Medium", "Hard", "Mixed"],
        index=3,
    )

    st.write(
        "The app retrieves relevant chunks from your selected document "
        "and asks Gemini to generate exactly 5 multiple-choice questions."
    )

    if st.button("🎯 Generate Quiz", type="primary"):
        reset_quiz()

        try:
            status = st.status(
                "Preparing your quiz...",
                expanded=True,
            )

            status.write("Retrieving relevant content from ChromaDB...")

            retrieval_query = (
                "Important facts, key concepts, definitions, "
                "processes, and main ideas in this document"
            )

            relevant_chunks = retrieve_relevant_chunks(
                query=retrieval_query,
                source=selected_pdf,
                top_k=RETRIEVAL_TOP_K,
            )

            if not relevant_chunks:
                status.update(
                    label="No relevant content found",
                    state="error",
                )
                st.error(
                    "No chunks were retrieved for this PDF. "
                    "Please process the document again."
                )

            else:
                status.write(
                    f"Retrieved {len(relevant_chunks)} relevant chunks."
                )
                status.write("Asking Gemini to generate 5 questions...")

                questions = generate_quiz(
                    relevant_chunks,
                    difficulty=difficulty,
                )

                st.session_state.quiz_questions = questions
                st.session_state.quiz_source = selected_pdf
                st.session_state.quiz_difficulty = difficulty
                st.session_state.quiz_submitted = False
                st.session_state.quiz_result = None

                status.update(
                    label="Quiz generated successfully!",
                    state="complete",
                    expanded=False,
                )

                st.rerun()

        except Exception as exc:
            st.error(f"Quiz generation failed: {exc}")
            st.caption(
                "Check the terminal for detailed ChromaDB or Gemini errors."
            )


# --------------------------------------------------
# 4. QUIZ INTERFACE
# --------------------------------------------------

questions = st.session_state.quiz_questions

if questions:
    st.divider()
    st.header("4. Take Your Quiz")

    st.write(f"**Document:** {st.session_state.quiz_source}")
    st.write(f"**Difficulty:** {st.session_state.quiz_difficulty}")
    st.write(f"**Total questions:** {len(questions)}")

    if not st.session_state.quiz_submitted:

        with st.form("quiz_form"):
            for index, question in enumerate(questions):
                st.subheader(
                    f"Question {index + 1} of {len(questions)}"
                )
                st.write(question["question"])

                options = question["options"]

                st.radio(
                    "Select your answer:",
                    options=["A", "B", "C", "D"],
                    format_func=lambda option, opts=options: (
                        f"{option}. {opts[option]}"
                    ),
                    index=None,
                    key=f"answer_{index}",
                )

                st.divider()

            submitted = st.form_submit_button(
                "✅ Submit Quiz",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            user_answers = {}

            for index in range(len(questions)):
                answer = st.session_state.get(f"answer_{index}")

                if answer:
                    user_answers[index] = answer

            try:
                result = evaluate_quiz(
                    questions,
                    user_answers,
                )

                st.session_state.quiz_result = result
                st.session_state.quiz_submitted = True
                st.rerun()

            except Exception as exc:
                st.error(f"Could not evaluate quiz: {exc}")


# --------------------------------------------------
# 5. QUIZ RESULTS AND ANSWER REVIEW
# --------------------------------------------------

if (
    st.session_state.quiz_submitted
    and st.session_state.quiz_result is not None
):
    result = st.session_state.quiz_result

    st.divider()
    st.header("5. Quiz Results")

    score = result["score"]
    total = result["total_questions"]
    percentage = result["percentage"]

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric(
        "Final Score",
        f"{score}/{total}",
    )

    result_col2.metric(
        "Percentage",
        f"{percentage:.0f}%",
    )

    result_col3.metric(
        "Correct Answers",
        f"{score} out of {total}",
    )

    st.progress(int(percentage))

    message = get_performance_message(score, total)
    st.success(message)

    st.subheader("Answer Review")

    for item in result["review"]:
        number = item["question_number"]

        if item["is_correct"]:
            st.success(f"Question {number}: Correct answer!")
        else:
            st.error(f"Question {number}: Incorrect answer.")

        st.write(item["question"])

        selected = item["selected_answer"]

        if selected:
            selected_text = item["options"].get(
                selected,
                "Unknown option",
            )
            st.write(f"**Your answer:** {selected}. {selected_text}")
        else:
            st.write("**Your answer:** Not answered")

        correct = item["correct_answer"]
        correct_text = item["correct_option_text"]

        st.write(f"**Correct answer:** {correct}. {correct_text}")

        if item.get("explanation"):
            st.write(f"**Explanation:** {item['explanation']}")

        st.divider()

    if st.button("🔄 Generate Another Quiz", type="primary"):
        reset_quiz()
        st.rerun()
