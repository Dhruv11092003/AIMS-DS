"""
mcq_question_bank.py
====================
Static MCQ question bank (PHQ-style) with difficulty levels
for baseline + RL adaptive questioning.
"""

MCQ_OPTIONS = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"}
]

MCQ_QUESTIONS = [
    # ----------------------------
    # EASY (general mood)
    # ----------------------------
    {
        "id": 1,
        "question": "Little interest or pleasure in doing things?",
        "difficulty": "easy",
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 2,
        "question": "Feeling down, depressed, or hopeless?",
        "difficulty": "easy",
        "scores": [0, 1, 2, 3]
    },

    # ----------------------------
    # MEDIUM (behavioral impact)
    # ----------------------------
    {
        "id": 3,
        "question": "Trouble falling or staying asleep, or sleeping too much?",
        "difficulty": "medium",
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 4,
        "question": "Feeling tired or having little energy?",
        "difficulty": "medium",
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 5,
        "question": "Poor appetite or overeating?",
        "difficulty": "medium",
        "scores": [0, 1, 2, 3]
    },

    # ----------------------------
    # HARD (cognitive / self-worth)
    # ----------------------------
    {
        "id": 6,
        "question": "Feeling bad about yourself — or that you are a failure?",
        "difficulty": "hard",
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 7,
        "question": "Trouble concentrating on things?",
        "difficulty": "hard",
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 8,
        "question": "Moving or speaking slowly, or being fidgety or restless?",
        "difficulty": "hard",
        "scores": [0, 1, 2, 3]
    }
]
