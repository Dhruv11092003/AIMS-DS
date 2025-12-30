"""
final_decision_service.py
=========================
Combines:
- Fusion model output
- MCQ psychometric score

Produces:
- Final confidence
- Final depression class
- Explanation-friendly output
"""

from app.services.mcq.mcq_scoring_service import compute_mcq_score

# ------------------------------------------------------
# WEIGHT CONFIG (LOCKED DEFAULTS)
# ------------------------------------------------------

ALPHA = 0.7  # behavioral (fusion)
BETA = 0.3   # MCQ

# ------------------------------------------------------
# FINAL DECISION FUNCTION
# ------------------------------------------------------

def compute_final_decision(
    fusion_output: dict,
    mcq_answers: dict
) -> dict:
    """
    fusion_output:
    {
        "predicted_class": str,
        "class_probabilities": {...},
        "behavioral_confidence": float
    }

    mcq_answers:
    {
        question_id: selected_option
    }
    """

    mcq_result = compute_mcq_score(mcq_answers)

    behavioral_confidence = fusion_output["behavioral_confidence"]
    mcq_score = mcq_result["mcq_score"]

    # -----------------------------
    # FINAL CONFIDENCE
    # -----------------------------
    final_confidence = (
        ALPHA * behavioral_confidence +
        BETA * mcq_score
    )

    # -----------------------------
    # FINAL CLASS (3-CLASS)
    # -----------------------------
    if final_confidence > 0.7:
        final_class = "Low"
    elif final_confidence >= 0.4:
        final_class = "Moderate"
    else:
        final_class = "High"

    return {
        "final_class": final_class,
        "final_confidence": float(final_confidence),
        "behavioral_confidence": float(behavioral_confidence),
        "mcq_score": float(mcq_score),
        "mcq_uncertainty": mcq_result["mcq_uncertainty"],
        "class_probabilities": fusion_output["class_probabilities"],
        "explanation": {
            "fusion_weight": ALPHA,
            "mcq_weight": BETA,
            "decision_rule": "weighted_confidence_thresholding"
        }
    }
