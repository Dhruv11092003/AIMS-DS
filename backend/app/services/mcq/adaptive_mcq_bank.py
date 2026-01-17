"""
Adaptive MCQ Bank
=================
Used ONLY when RL is activated.

Purpose:
- Reduce uncertainty between Low / Moderate / High classes
- Target emotional exhaustion, hopelessness, cognitive load
"""

ADAPTIVE_MCQS = {

    # --------------------------------------------------
    # EASY — Clarifies LOW vs MODERATE
    # --------------------------------------------------
    "easy": [
        {
            "id": 501,
            "question": "Over the past week, how often did you feel calm or relaxed?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 502,
            "question": "Over the past week, how often did you feel satisfied with your daily activities?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 503,
            "question": "Over the past week, how often did you feel able to concentrate without effort?",
            "options": [0, 1, 2, 3]
        }
    ],

    # --------------------------------------------------
    # MEDIUM — Clarifies MODERATE ambiguity
    # --------------------------------------------------
    "medium": [
        {
            "id": 601,
            "question": "Over the past week, how often did you feel mentally exhausted?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 602,
            "question": "Over the past week, how often did you feel overwhelmed by responsibilities?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 603,
            "question": "Over the past week, how often did you feel emotionally drained after social interaction?",
            "options": [0, 1, 2, 3]
        }
    ],

    # --------------------------------------------------
    # HARD — Disambiguates HIGH severity
    # --------------------------------------------------
    "hard": [
        {
            "id": 701,
            "question": "Over the past week, how often did you feel emotionally drained or hopeless?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 702,
            "question": "Over the past week, how often did you feel that things would not improve?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 703,
            "question": "Over the past week, how often did you feel disconnected or numb?",
            "options": [0, 1, 2, 3]
        }
    ]
}
