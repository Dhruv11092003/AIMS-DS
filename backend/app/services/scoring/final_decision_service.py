"""
final_decision_service.py
=========================
Final decision logic for AIMS-DS.

Rules:
- Class is NEVER forced by thresholds
- Class = argmax of aggregated fusion probabilities
- Confidence determines stopping, not class
"""

from collections import defaultdict
from app.services.mcq.mcq_scoring_service import compute_mcq_score

ALPHA = 0.45  # Fusion weight
BETA = 0.65   # MCQ weight


def _aggregate_fusion_probabilities(questions: list) -> dict:
    """
    Aggregates class probabilities across all video questions.
    """
    if not questions:
        return {}

    agg = defaultdict(float)
    count = 0

    for q in questions:
        probs = q.get("fusion_output", {}).get("class_probabilities")
        if not probs:
            continue

        for cls, p in probs.items():
            agg[cls] += p

        count += 1

    if count == 0:
        return {}

    return {k: v / count for k, v in agg.items()}


def compute_final_decision(
    session: dict
) -> dict:
    """
    Uses:
    - Aggregated fusion probabilities
    - Behavioral confidence
    - MCQ score & uncertainty
    """

    # --------------------------------------------------
    # FUSION AGGREGATION
    # --------------------------------------------------
    fusion_probs = _aggregate_fusion_probabilities(
        session.get("questions", [])
    )

    if not fusion_probs:
        raise ValueError("Fusion class probabilities missing")

    final_class = max(fusion_probs, key=fusion_probs.get)

    behavioral_confidence = sum(
        q["fusion_output"]["behavioral_confidence"]
        for q in session["questions"]
    ) / len(session["questions"])

    # --------------------------------------------------
    # MCQ
    # --------------------------------------------------
    mcq_result = compute_mcq_score(session.get("mcq_answers", {}))
    mcq_score = mcq_result["mcq_score"]
    mcq_uncertainty = mcq_result["mcq_uncertainty"]

    mcq_effective = mcq_score * (1 - mcq_uncertainty)

    # --------------------------------------------------
    # FINAL CONFIDENCE
    # --------------------------------------------------
    final_confidence = (
        ALPHA * behavioral_confidence +
        BETA * mcq_effective
    )

    return {
        "final_class": final_class,
        "final_confidence": float(final_confidence),
        "behavioral_confidence": float(behavioral_confidence),
        "mcq_score": float(mcq_score),
        "mcq_uncertainty": float(mcq_uncertainty),
        "class_probabilities": fusion_probs,
        "explanation": {
            "fusion_weight": ALPHA,
            "mcq_weight": BETA,
            "decision_rule": "fusion_with_weighted_confidence"
        }
    }
