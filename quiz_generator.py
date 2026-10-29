
import json
import re
import time

from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    QUIZ_QUESTION_COUNT,
    validate_gemini_config,
)


def _extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Gemini returned an empty response.")

    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError(
                "Could not find valid JSON in Gemini's response."
            )

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON. Please try again."
            ) from exc


def _validate_questions(data: dict) -> list[dict]:
    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("The response does not contain a questions list.")

    if len(questions) != QUIZ_QUESTION_COUNT:
        raise ValueError(
            f"Expected exactly {QUIZ_QUESTION_COUNT} questions, "
            f"but received {len(questions)}."
        )

    validated = []

    for index, item in enumerate(questions, start=1):
        question_text = str(item.get("question", "")).strip()
        options = item.get("options", {})
        correct_answer = str(
            item.get("correct_answer", "")
        ).strip().upper()

        if not question_text:
            raise ValueError(f"Question {index} has no question text.")

        if not isinstance(options, dict):
            raise ValueError(f"Question {index} has invalid options.")

        normalized_options = {
            key: str(options.get(key, "")).strip()
            for key in ["A", "B", "C", "D"]
        }

        if any(not value for value in normalized_options.values()):
            raise ValueError(
                f"Question {index} must have four non-empty options."
            )

        if correct_answer not in {"A", "B", "C", "D"}:
            raise ValueError(
                f"Question {index} has an invalid correct answer."
            )

        validated.append({
            "question": question_text,
            "options": normalized_options,
            "correct_answer": correct_answer,
            "explanation": str(item.get("explanation", "")).strip(),
        })

    return validated


def generate_quiz(
    retrieved_chunks: list[dict],
    difficulty: str = "Mixed",
) -> list[dict]:

    if not retrieved_chunks:
        raise ValueError(
            "No relevant document content was retrieved. "
            "Please process the PDF again."
        )

    validate_gemini_config()

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"Source: {chunk.get('source', 'Unknown')}\n"
            f"Page: {chunk.get('page_number', 'Unknown')}\n"
            f"Content:\n{chunk.get('text', '')}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are an educational quiz generator.

Use ONLY the PDF content supplied below.

Generate exactly {QUIZ_QUESTION_COUNT} distinct multiple-choice questions.
Difficulty: {difficulty}

Requirements:
1. Every question must be answerable from the supplied content.
2. Each question must have exactly four options: A, B, C, and D.
3. Only one option must be correct.
4. Avoid repeating the same question.
5. Include a short explanation grounded in the document.
6. Return valid JSON only, with no Markdown or text outside the JSON.

Required JSON format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation based on the document"
    }}
  ]
}}

PDF CONTENT:
{context}
"""

    client = genai.Client(api_key=GEMINI_API_KEY)

    print(f"\nSending quiz request to Gemini model: {GEMINI_MODEL}")
    start_time = time.time()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

    except Exception as exc:
        elapsed = time.time() - start_time
        print(f"Gemini request failed after {elapsed:.2f} seconds.")
        print(f"Gemini error: {exc}")

        raise RuntimeError(
            "Gemini could not generate the quiz. "
            "Check the terminal for the detailed error. "
            "Verify that your API key is valid and the configured model "
            "is available to your account."
        ) from exc

    print(f"Gemini responded in {time.time() - start_time:.2f} seconds.")

    response_text = getattr(response, "text", None)

    if not response_text:
        raise ValueError(
            "Gemini returned no text. Please check the model response "
            "and try again."
        )

    data = _extract_json(response_text)
    questions = _validate_questions(data)

    print(f"Successfully generated {len(questions)} questions.")
    return questions
