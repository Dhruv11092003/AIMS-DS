"""
rl_video_selector.py
====================
Selects adaptive RL video questions.
"""

# Simple adaptive RL video question pool
RL_VIDEO_QUESTIONS = {
    "easy": [
        {"id": 101, "question": "How have you been feeling emotionally this week?"}
    ],
    "medium": [
        {"id": 201, "question": "Can you describe a recent situation that caused you stress?"}
    ],
    "hard": [
        {"id": 301, "question": "Have you experienced feelings of hopelessness or lack of purpose recently?"}
    ]
}


def select_rl_video_question(difficulty: str, asked_video_ids: list):
    """
    Select an RL video question based on difficulty,
    avoiding already asked video questions.
    """
    candidates = [
        q for q in RL_VIDEO_QUESTIONS.get(difficulty, [])
        if q["id"] not in asked_video_ids
    ]

    if not candidates:
        return None

    return candidates[0]  # deterministic
