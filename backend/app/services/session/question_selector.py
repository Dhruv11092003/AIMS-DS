import random
from app.services.session.video_question_bank import VIDEO_QUESTIONS
from app.services.mcq.adaptive_mcq_bank import ADAPTIVE_MCQS


def select_baseline_video_question(asked_ids: list):
    """
    Always exhaust baseline questions first.
    """
    for q in VIDEO_QUESTIONS["baseline"]:
        if q["id"] not in asked_ids:
            return q
    return None


# def select_rl_video_question(difficulty: str, asked_ids: list):
#     """
#     Select an RL-driven video question by difficulty.
#     """
#     pool = VIDEO_QUESTIONS.get(difficulty, [])
#     remaining = [q for q in pool if q["id"] not in asked_ids]
#     return random.choice(remaining) if remaining else None


# def select_rl_mcq(difficulty: str):
#     """
#     Select an RL-driven MCQ.
#     """
#     pool = ADAPTIVE_MCQS.get(difficulty, [])
#     return random.choice(pool) if pool else None
