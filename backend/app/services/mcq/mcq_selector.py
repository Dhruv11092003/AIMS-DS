from app.services.mcq.adaptive_mcq_bank import ADAPTIVE_MCQS


def select_rl_mcq(difficulty: str, session: dict):
    """
    Select an adaptive MCQ for the RL phase based on difficulty,
    avoiding already answered questions. Falls back to the other
    difficulty buckets if the requested one is exhausted, so a
    few repeated picks by the policy don't starve the RL phase.
    """

    asked = set(session.get("asked_mcqs", []))

    ordered_buckets = [difficulty] + [
        d for d in ("easy", "medium", "hard") if d != difficulty
    ]

    for bucket_name in ordered_buckets:
        bucket = ADAPTIVE_MCQS.get(bucket_name, [])
        for q in bucket:
            if q["id"] not in asked:
                return q

    return None
