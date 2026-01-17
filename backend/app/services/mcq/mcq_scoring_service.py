"""
MCQ / PHQ-8 scoring service (STAGE 6 – SEQUENTIAL EVIDENCE MODEL).

Key properties:
- No hard-coded score buckets
- Sequential Bayesian-style evidence accumulation
- Smoothly evolving class probabilities
- Entropy-based uncertainty suitable for RL
"""

import math

EPS = 1e-9
CLASS_LABELS = ["Low", "Moderate", "High"]

# Maximum baseline PHQ-8 questions
MAX_BASELINE_QUESTIONS = 8


# ======================================================
# ANSWER → LIKELIHOOD MAPPING
# ======================================================
# Each answer softly votes for severity classes.
# Values are relative likelihoods (not probabilities).

ANSWER_LIKELIHOODS = {
    0: {"Low": 0.70, "Moderate": 0.20, "High": 0.10},  # Not at all
    1: {"Low": 0.45, "Moderate": 0.40, "High": 0.15},  # Several days
    2: {"Low": 0.20, "Moderate": 0.50, "High": 0.30},  # More than half the days
    3: {"Low": 0.10, "Moderate": 0.30, "High": 0.60},  # Nearly every day
}


# ======================================================
# HELPERS
# ======================================================

def _normalize(dist: dict) -> dict:
    total = sum(dist.values())
    if total <= 0:
        return {k: 1.0 / len(dist) for k in dist}
    return {k: v / total for k, v in dist.items()}


def _entropy(dist: dict) -> float:
    vals = [max(v, EPS) for v in dist.values()]
    h = -sum(v * math.log(v) for v in vals)
    return h / math.log(len(vals))  # normalized [0,1]


# ======================================================
# MAIN ENTRY
# ======================================================

def compute_mcq_score(mcq_answers: dict) -> dict:
    """
    Sequentially computes psychometric class probabilities from PHQ-8 answers.

    Args:
        mcq_answers (dict): {question_id: answer_value (0–3)}

    Returns:
        {
            "mcq_score": float,
            "mcq_uncertainty": float,
            "mcq_probabilities": dict
        }
    """

    # --------------------------------------------------
    # NO ANSWERS → UNIFORM PRIOR
    # --------------------------------------------------
    if not mcq_answers or len(mcq_answers) == 0:
        uniform = {"Low": 0.33, "Moderate": 0.33, "High": 0.34}
        return {
            "mcq_score": 0.0,
            "mcq_uncertainty": 1.0,
            "mcq_probabilities": uniform
        }

    # --------------------------------------------------
    # INITIAL PRIOR
    # --------------------------------------------------
    probs = {"Low": 0.33, "Moderate": 0.33, "High": 0.34}

    total_score = 0.0

    # --------------------------------------------------
    # SEQUENTIAL BAYESIAN UPDATE
    # --------------------------------------------------
    for _, answer in mcq_answers.items():
        answer = int(answer)
        total_score += answer

        likelihood = ANSWER_LIKELIHOODS.get(answer)
        if likelihood is None:
            continue

        # Multiply likelihood (Bayesian update)
        for cls in CLASS_LABELS:
            probs[cls] *= likelihood[cls]

        probs = _normalize(probs)

    # --------------------------------------------------
    # UNCERTAINTY (ENTROPY-BASED)
    # --------------------------------------------------
    entropy = _entropy(probs)

    # Normalize uncertainty relative to number of questions answered
    # More answers → lower uncertainty
    progress_factor = min(len(mcq_answers) / MAX_BASELINE_QUESTIONS, 1.0)
    mcq_uncertainty = entropy * (1.0 - 0.3 * progress_factor)

    # --------------------------------------------------
    # MCQ SCORE (FOR LOGGING / INTERPRETABILITY)
    # --------------------------------------------------
    mcq_score = total_score / len(mcq_answers)

    return {
        "mcq_score": float(mcq_score),
        "mcq_uncertainty": float(mcq_uncertainty),
        "mcq_probabilities": probs
    }
