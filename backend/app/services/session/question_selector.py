from app.services.session.video_question_bank import VIDEO_QUESTIONS


def select_baseline_video_question(asked_ids: list):
    """
    Always exhaust baseline questions first.
    """
    for q in VIDEO_QUESTIONS["baseline"]:
        if q["id"] not in asked_ids:
            return q
    return None


def select_rl_video_question(difficulty: str, asked_ids: list):
    """
    Select an RL-driven video question by difficulty, avoiding
    questions already asked in this session. Falls back to the
    other difficulty pools if the requested one is exhausted so
    the RL agent doesn't get starved mid-session.
    """
    ordered_pools = [difficulty] + [
        d for d in ("easy", "medium", "hard") if d != difficulty
    ]

    for pool_name in ordered_pools:
        pool = VIDEO_QUESTIONS.get(pool_name, [])
        for q in pool:
            if q["id"] not in asked_ids:
                return q

    return None
