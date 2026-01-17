"""
RL state builder for AIMS-DS (STAGE 4 – IMPLEMENTATION).

Objective:
- Expose Bayesian uncertainty and disagreement to the RL agent
- Normalize all features to [0, 1] for stability
- Preserve API contract: build_rl_state(session) -> np.ndarray

State Vector (normalized):
[ 0] current_entropy                 ∈ [0, 1]
[ 1] entropy_delta                   ∈ [0, 1]  (progress signal)
[ 2] disagreement_kl_norm            ∈ [0, 1]
[ 3] progress_ratio                  ∈ [0, 1]  (#steps / max)
[ 4] p_low                           ∈ [0, 1]
[ 5] p_moderate                      ∈ [0, 1]
[ 6] p_high                          ∈ [0, 1]
"""

import numpy as np

# ======================================================
# CONFIGURATION
# ======================================================

MAX_QUESTIONS = 5          # fatigue budget
MAX_KL_EXPECTED = 1.5      # soft cap for normalization
EPS = 1e-8

CLASS_LABELS = ["Low", "Moderate", "High"]


# ======================================================
# NORMALIZATION HELPERS
# ======================================================

def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def _normalize_kl(kl: float) -> float:
    """
    Normalizes KL divergence into [0, 1] range.
    """
    return _clip01(kl / MAX_KL_EXPECTED)


# ======================================================
# MAIN STATE BUILDER (PUBLIC CONTRACT)
# ======================================================

def build_rl_state(session: dict) -> np.ndarray:
    """
    Builds a normalized RL state vector from the session.

    Expected session fields (from Stage 2):
    - session["final_decision"]:
        {
            "final_probabilities": dict,
            "uncertainty_level": float,
            "diagnostics": {
                "behavioral_probabilities": dict,
                "psychometric_probabilities": dict,
                "disagreement_kl": float
            }
        }

    Returns:
        np.ndarray of shape (7,)
    """

    # --------------------------------------------------
    # SAFE DEFAULT (NO DECISION YET)
    # --------------------------------------------------
    final_decision = session.get("final_decision")
    if not final_decision:
        return np.zeros(7, dtype=np.float32)

    # --------------------------------------------------
    # CORE BAYESIAN SIGNALS
    # --------------------------------------------------
    current_entropy = _clip01(
        final_decision.get("uncertainty_level", 1.0)
    )

    diagnostics = final_decision.get("diagnostics", {})
    disagreement_kl = _normalize_kl(
        diagnostics.get("disagreement_kl", 0.0)
    )

    final_probs = final_decision.get("final_probabilities", {})
    p_low = _clip01(final_probs.get("Low", 0.0))
    p_mod = _clip01(final_probs.get("Moderate", 0.0))
    p_high = _clip01(final_probs.get("High", 0.0))

    # --------------------------------------------------
    # TEMPORAL AWARENESS (ENTROPY DELTA)
    # --------------------------------------------------
    prev_entropy = session.get("prev_uncertainty_level")
    if prev_entropy is None:
        entropy_delta = 0.0
    else:
        # Positive delta = improvement (entropy reduction)
        entropy_delta = _clip01(prev_entropy - current_entropy)

    # Store for next step (side-effect is intentional and local)
    session["prev_uncertainty_level"] = current_entropy

    # --------------------------------------------------
    # PROGRESS / FATIGUE SIGNAL
    # --------------------------------------------------
    steps_taken = session.get("rl_steps", 0)
    progress_ratio = _clip01(steps_taken / MAX_QUESTIONS)

    # --------------------------------------------------
    # FINAL STATE VECTOR
    # --------------------------------------------------
    state = np.array([
        current_entropy,      # replaces avg_confidence
        entropy_delta,        # replaces confidence_delta
        disagreement_kl,      # new but critical
        progress_ratio,       # fatigue awareness
        p_high                # strongest class signal
    ], dtype=np.float32)

    return state
