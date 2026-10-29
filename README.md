# 📚 RAG-Based PDF Quiz Generator

An AI-powered web application that transforms PDF documents into interactive multiple-choice quizzes using **Retrieval-Augmented Generation (RAG)**, **ChromaDB**, and **Google Gemini**.

Upload a PDF, retrieve relevant information from its content, generate exactly five MCQs, and evaluate your answers with instant feedback.

## ✨ Features

- 📄 **PDF Upload:** Upload and process PDF documents.
- 📝 **Text Extraction:** Extract readable text using PyMuPDF.
- ✂️ **Text Chunking:** Split text into manageable chunks with configurable overlap.
- 🗄️ **Vector Storage:** Store document chunks in a persistent ChromaDB database.
- 🔍 **Semantic Retrieval:** Retrieve relevant document chunks for question generation.
- 🤖 **AI-Powered Quiz Generation:** Generate five document-grounded MCQs using Google Gemini.
- 🎯 **Interactive Quiz:** Answer questions using radio buttons with four options (A, B, C, and D).
- 📊 **Automatic Evaluation:** Calculate scores and percentages instantly.
- ✅ **Answer Review:** View correct answers, incorrect responses, and explanations.
- 💾 **Local Persistence:** Retain processed document chunks between application sessions.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| PyMuPDF | PDF text extraction |
| LangChain Text Splitters | Text chunking |
| ChromaDB | Vector database and retrieval |
| Google Gemini API | AI question generation |
| python-dotenv | Environment variable management |

## 🏗️ System Architecture

The application follows a Retrieval-Augmented Generation pipeline:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Text Chunking
    ↓
ChromaDB Vector Storage
    ↓
Relevant Chunk Retrieval
    ↓
Google Gemini
    ↓
5 Multiple-Choice Questions
    ↓
Answer Submission
    ↓
Score Calculation and Results
```

## 📁 Project Structure

```text
RAG-QUIZ-APP/
├── app.py
├── config.py
├── pdf_processor.py
├── vector_store.py
├── quiz_generator.py
├── quiz_evaluator.py
├── utils.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env  # Local only; never upload
```

## ⚙️ Installation and Setup

### 1. Clone the repository

Replace `YOUR-REPOSITORY-NAME` with your actual GitHub repository name.

```bash
git clone https://github.com/akankshariyasingh/YOUR-REPOSITORY-NAME.git
cd YOUR-REPOSITORY-NAME
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model
```

Get your API key from [Google AI Studio](https://aistudio.google.com/). Set `GEMINI_MODEL` to a model supported by your API key.

**Security:** Never commit your real API key or `.env` file to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## 📊 Quiz Evaluation

After submitting the quiz, the application displays:

- Final score out of five questions
- Overall percentage
- Correct or incorrect status for each response
- Selected answer and correct answer
- Explanations to support learning

For example, four correct answers out of five result in a score of **4/5 (80%)**.

## 🔐 Security and Storage

- API credentials are stored in environment variables.
- `.env`, `venv/`, and `chroma_db/` should be excluded from version control.
- The vector database is stored locally.
- Document content included in a quiz-generation request is sent to the configured Gemini API.

## 🚀 Future Improvements

- OCR support for scanned PDFs.
- Topic-specific quiz generation.
- Quiz history and performance tracking.
- Configurable question counts.
- Source-page references for generated questions.
- Cloud deployment.

## 👩‍💻 Author

**Akanksha Singh**

B.Tech — Artificial Intelligence and Machine Learning

GitHub: [@akankshariyasingh](https://github.com/akankshariyasingh)

---

*Built to explore Retrieval-Augmented Generation, vector databases, document processing, and LLM-powered educational applications.*
