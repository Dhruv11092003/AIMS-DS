"""
mcq_scoring_service.py
=====================
Computes MCQ-based psychometric score and uncertainty.

MCQs are treated as a SEPARATE signal (not fused into ML features).
"""

import numpy as np

# ------------------------------------------------------
# MCQ CONFIG (EDITABLE, EXPLAINABLE)
# ------------------------------------------------------

# Example scale:
# 0 = Not at all
# 1 = Several days
# 2 = More than half the days
# 3 = Nearly every day

MCQ_RISK_WEIGHTS = {
    # question_id: weight
    1: 1.0,
    2: 1.2,
    3: 1.1,
    4: 1.3,
    5: 1.4,
    6: 1.2,
    7: 1.5,
    8: 1.3,
}

MAX_OPTION_SCORE = 3  # highest option value

# ------------------------------------------------------
# MAIN MCQ SCORING FUNCTION
# ------------------------------------------------------

def compute_mcq_score(mcq_answers: dict) -> dict:
    """
    mcq_answers example:
    {
        1: 2,
        2: 1,
        3: 3,
        ...
    }

    Returns:
    {
        "mcq_score": float (0–1),
        "mcq_uncertainty": float (0–1),
        "raw_score": float
    }
    """

    weighted_scores = []
    max_possible = 0
    neutral_count = 0

    for q_id, answer in mcq_answers.items():
        weight = MCQ_RISK_WEIGHTS.get(q_id, 1.0)

        weighted_scores.append(answer * weight)
        max_possible += MAX_OPTION_SCORE * weight

        if answer in [1, 2]:  # ambiguous mid-range answers
            neutral_count += 1


    raw_score = sum(weighted_scores)
    mcq_score = raw_score / max_possible if max_possible > 0 else 0.0

    # Uncertainty = proportion of neutral answers
    mcq_uncertainty = neutral_count / len(mcq_answers)

    return {
        "mcq_score": float(mcq_score),
        "mcq_uncertainty": float(mcq_uncertainty),
        "raw_score": float(raw_score)
    }
