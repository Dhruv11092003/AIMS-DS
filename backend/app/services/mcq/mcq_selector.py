from app.services.mcq.question_bank import MCQ_QUESTIONS

def select_rl_mcq(difficulty: str, session: dict):
    """
    Select an RL MCQ based on difficulty,
    avoiding already asked MCQs.
    """

    asked_mcqs = set(session.get("asked_mcqs", []))

    candidates = [
        q for q in MCQ_QUESTIONS
        if q["difficulty"] == difficulty
        and q["id"] not in asked_mcqs
    ]

    if not candidates:
        return None

    return candidates[0]  # deterministic for now
