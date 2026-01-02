"""
Video Question Bank
Baseline + RL-adaptive video questions.
"""

VIDEO_QUESTIONS = {
    # ---------------- BASELINE (ASK ALL FIRST) ----------------
    "baseline": [
        {"id": 1, "text": "Tell me about yourself and how you have been feeling recently."},
        {"id": 2, "text": "Can you describe a recent challenge you faced in your daily life?"},
        {"id": 3, "text": "How do you usually cope when you feel stressed or overwhelmed?"},
        {"id": 4, "text": "How has your mood been over the past few days?"}
    ],

    # ---------------- RL-ADAPTIVE ----------------
    "easy": [
        {"id": 101, "text": "What do you usually like to do in your free time?"},
        {"id": 102, "text": "Can you describe what a typical day looks like for you?"}
    ],

    "medium": [
        {"id": 201, "text": "Describe a situation where you recently felt mentally tired."},
        {"id": 202, "text": "How do you react when things do not go as planned?"}
    ],

    "hard": [
        {"id": 301, "text": "Tell me about a time you felt emotionally drained or stuck."},
        {"id": 302, "text": "How do you cope with prolonged feelings of sadness or stress?"}
    ]
}
