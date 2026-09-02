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
        },
        {
            "id": 504,
            "question": "Over the past week, how often did you look forward to things during the day?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 505,
            "question": "Over the past week, how often did you feel comfortable talking to people around you?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 506,
            "question": "Over the past week, how often did you feel physically rested after sleeping?",
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
        },
        {
            "id": 604,
            "question": "Over the past week, how often did you find it hard to start everyday tasks?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 605,
            "question": "Over the past week, how often did small setbacks feel harder to deal with than usual?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 606,
            "question": "Over the past week, how often did you withdraw from people you'd normally talk to?",
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
        },
        {
            "id": 704,
            "question": "Over the past week, how often did you feel persistently low for most of the day?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 705,
            "question": "Over the past week, how often did you feel unable to enjoy things you used to enjoy at all?",
            "options": [0, 1, 2, 3]
        },
        {
            "id": 706,
            "question": "Over the past week, how often did you feel like nothing you did mattered?",
            "options": [0, 1, 2, 3]
        }
    ]
}
