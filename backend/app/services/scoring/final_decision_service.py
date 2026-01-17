"""
Final decision logic for AIMS-DS (ROBUST + MCQ-GATED).

Fixes:
- Correct entropy calibration for 3-class problem
- Prevents premature finalization before MCQs
- Forces RL when psychometric evidence is absent
"""

from collections import defaultdict
import math
from app.services.mcq.mcq_scoring_service import compute_mcq_score

EPS = 1e-9
CLASS_LABELS = ["Low", "Moderate", "High"]

# Bayesian base weights
ALPHA_BEHAVIORAL = 0.4
BETA_PSYCHOMETRIC = 0.6

# 🔥 Correct entropy threshold (normalized)
ENTROPY_TRIGGER_THRESHOLD = 0.45

# Extreme dominance threshold (video-only escape hatch)
VIDEO_DOMINANCE_THRESHOLD = 0.95


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def _normalize(dist: dict) -> dict:
    s = sum(dist.values())
    if s <= 0:
        return {k: 1.0 / len(dist) for k in dist}
    return {k: v / s for k, v in dist.items()}


def _entropy(dist: dict) -> float:
    vals = [max(v, EPS) for v in dist.values()]
    h = -sum(v * math.log(v) for v in vals)
    return h / math.log(len(vals))  # normalized [0,1]


def _kl(p: dict, q: dict) -> float:
    kl = 0.0
    for k in p:
        p_val = max(p[k], EPS)
        q_val = max(q.get(k, EPS), EPS)
        kl += p_val * math.log(p_val / q_val)
    return kl


def _aggregate_fusion_probs(questions: list) -> dict:
    agg = defaultdict(float)
    count = 0
    for q in questions:
        probs = q.get("fusion_output", {}).get("class_probabilities")
        if not probs:
            continue
        for cls, p in probs.items():
            agg[cls] += float(p)
        count += 1

    if count == 0:
        raise ValueError("No fusion probabilities available")

    return {k: v / count for k, v in agg.items()}


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def compute_final_decision(session: dict) -> dict:
    # ------------------------------
    # BEHAVIORAL (VIDEO) EVIDENCE
    # ------------------------------
    behavioral_probs = _normalize(
        _aggregate_fusion_probs(session.get("questions", []))
    )

    behavioral_confidence = sum(
        q["fusion_output"]["behavioral_confidence"]
        for q in session["questions"]
    ) / len(session["questions"])

    max_video_prob = max(behavioral_probs.values())

    # ------------------------------
    # MCQ EVIDENCE (SAFE)
    # ------------------------------
    mcq_result = compute_mcq_score(session.get("mcq_answers", {}))
    mcq_probs = mcq_result["mcq_probabilities"]
    mcq_uncertainty = mcq_result["mcq_uncertainty"]

    # ------------------------------
    # BAYESIAN AGGREGATION
    # ------------------------------
    if mcq_uncertainty >= 1.0:
        # No MCQs yet → behavioral only
        final_probs = behavioral_probs
        disagreement = 0.0
    else:
        alpha = ALPHA_BEHAVIORAL + 0.2 * behavioral_confidence
        alpha = min(max(alpha, 0.3), 0.6)
        beta = 1.0 - alpha

        combined = {
            cls: alpha * behavioral_probs.get(cls, 0.0)
               + beta * mcq_probs.get(cls, 0.0)
            for cls in CLASS_LABELS
        }

        final_probs = _normalize(combined)
        disagreement = _kl(behavioral_probs, mcq_probs)

    # ------------------------------
    # UNCERTAINTY LOGIC (FIXED)
    # ------------------------------
    entropy = _entropy(final_probs)

    # 🔒 Mandatory MCQ rule
    if mcq_uncertainty >= 1.0 and max_video_prob < VIDEO_DOMINANCE_THRESHOLD:
        needs_rl_refinement = True
    else:
        needs_rl_refinement = entropy >= ENTROPY_TRIGGER_THRESHOLD

    final_class = max(final_probs, key=final_probs.get)

    return {
        "final_class": final_class,
        "final_probabilities": final_probs,
        "uncertainty_level": float(entropy),
        "needs_rl_refinement": bool(needs_rl_refinement),
        "diagnostics": {
            "behavioral_probabilities": behavioral_probs,
            "psychometric_probabilities": mcq_probs,
            "behavioral_confidence": float(behavioral_confidence),
            "mcq_uncertainty": float(mcq_uncertainty),
            "max_video_probability": float(max_video_prob),
            "disagreement_kl": float(disagreement)
        }
    }
