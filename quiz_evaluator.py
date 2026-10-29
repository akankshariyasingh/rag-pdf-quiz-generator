
def evaluate_quiz(
    questions: list[dict],
    user_answers: dict[int, str],
) -> dict:
    """
    Evaluate quiz answers and return the score and answer review.

    Args:
        questions: List of validated questions from quiz_generator.py.
        user_answers: Dictionary mapping question indexes to selected
                      option letters, such as {0: "A", 1: "C"}.

    Returns:
        Dictionary containing score, percentage, and detailed review.
    """
    if not isinstance(questions, list):
        raise TypeError("Questions must be provided as a list.")

    if not isinstance(user_answers, dict):
        raise TypeError("User answers must be provided as a dictionary.")

    total_questions = len(questions)

    if total_questions == 0:
        raise ValueError("There are no questions to evaluate.")

    score = 0
    review = []

    for index, question in enumerate(questions):
        correct_answer = str(
            question.get("correct_answer", "")
        ).strip().upper()

        selected_answer = str(
            user_answers.get(index, "")
        ).strip().upper()

        options = question.get("options", {})
        is_correct = (
            selected_answer == correct_answer
            and selected_answer in {"A", "B", "C", "D"}
        )

        if is_correct:
            score += 1

        review.append(
            {
                "question_number": index + 1,
                "question": question.get("question", ""),
                "options": options,
                "selected_answer": selected_answer or None,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "correct_option_text": options.get(
                    correct_answer, ""
                ),
                "explanation": question.get("explanation", ""),
            }
        )

    percentage = round((score / total_questions) * 100, 2)

    return {
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "review": review,
    }


def get_performance_message(score: int, total: int) -> str:
    """Return a simple message based on the quiz result."""
    if total <= 0:
        return "No questions were evaluated."

    percentage = (score / total) * 100

    if percentage == 100:
        return "Excellent! You answered every question correctly."
    elif percentage >= 80:
        return "Great work! You have a strong understanding."
    elif percentage >= 60:
        return "Good effort! Review the incorrect answers to improve."
    elif percentage >= 40:
        return "Keep practicing. Revisit the PDF and try again."
    else:
        return "Review the document carefully and give it another try."
