"""
Adaptive MCQ Bank
Used ONLY when RL is activated.
"""

ADAPTIVE_MCQS = {
    "easy": [
        {
            "id": 501,
            "question": "Over the past week, how often did you feel calm or relaxed?",
            "options": [0, 1, 2, 3]
        }
    ],

    "medium": [
        {
            "id": 601,
            "question": "Over the past week, how often did you feel mentally exhausted?",
            "options": [0, 1, 2, 3]
        }
    ],

    "hard": [
        {
            "id": 701,
            "question": "Over the past week, how often did you feel emotionally drained or hopeless?",
            "options": [0, 1, 2, 3]
        }
    ]
}
