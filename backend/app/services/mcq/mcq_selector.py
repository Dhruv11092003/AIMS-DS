from app.services.mcq.adaptive_mcq_bank import ADAPTIVE_MCQS


def select_rl_mcq(difficulty: str, session: dict):
    """
    Select an adaptive MCQ for RL phase based on difficulty,
    avoiding already answered questions.
    """

    asked = set(session.get("asked_mcqs", []))

    # -----------------------------
    # SAFE DIFFICULTY FALLBACK
    # -----------------------------
    bucket = ADAPTIVE_MCQS.get(difficulty)

    if not bucket:
        bucket = ADAPTIVE_MCQS.get("medium", [])

    # -----------------------------
    # FILTER UNASKED QUESTIONS
    # -----------------------------
    candidates = [
        q for q in bucket
        if q["id"] not in asked
    ]

    if not candidates:
        return None

    # Deterministic for now (can randomize later)
    return candidates[0]
