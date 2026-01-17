"""
RL reward function for AIMS-DS (STAGE 3 – IMPLEMENTATION).

Objective:
- Reward INFORMATION GAIN, not raw confidence
- Penalize redundancy / user fatigue
- Encourage reconciliation between behavioral (fusion) and PHQ evidence

Reward Components:
1) Entropy Reduction:
   R_entropy = H(prev) - H(current)

2) Redundancy Penalty:
   R_step = -lambda_step

3) Disagreement Reduction Bonus:
   R_kl = +gamma * (KL_prev - KL_current)

Total Reward:
   R = R_entropy + R_kl - R_step
"""

import math

EPS = 1e-9

# Tunable coefficients (safe defaults)
STEP_PENALTY = 0.05        # discourages long interviews
KL_BONUS_WEIGHT = 0.3      # reward for reconciling disagreement
NO_PROGRESS_PENALTY = 0.05 # penalty if uncertainty stagnates or increases


# ======================================================
# INFORMATION-THEORETIC HELPERS
# ======================================================

def _shannon_entropy(prob_dist: dict) -> float:
    """
    Normalized Shannon entropy in [0, 1].
    """
    values = [max(v, EPS) for v in prob_dist.values()]
    entropy = -sum(v * math.log(v) for v in values)
    max_entropy = math.log(len(values))
    return entropy / max_entropy


def _kl_divergence(p: dict, q: dict) -> float:
    """
    KL(p || q) with numerical safety.
    """
    kl = 0.0
    for cls in p:
        p_val = max(p.get(cls, EPS), EPS)
        q_val = max(q.get(cls, EPS), EPS)
        kl += p_val * math.log(p_val / q_val)
    return kl


# ======================================================
# MAIN REWARD FUNCTION (PUBLIC CONTRACT)
# ======================================================

def compute_reward(prev_state: dict, new_state: dict, action: int, done: bool) -> float:
    """
    Computes RL reward based on entropy reduction and disagreement reconciliation.

    Expected state structure (from Stage 2):
    {
        "final_probabilities": dict,
        "uncertainty_level": float,
        "diagnostics": {
            "behavioral_probabilities": dict,
            "psychometric_probabilities": dict,
            "disagreement_kl": float
        }
    }
    """

    reward = 0.0

    # --------------------------------------------------
    # ENTROPY REDUCTION (PRIMARY OBJECTIVE)
    # --------------------------------------------------
    prev_entropy = prev_state.get("uncertainty_level")
    new_entropy = new_state.get("uncertainty_level")

    if prev_entropy is not None and new_entropy is not None:
        entropy_gain = prev_entropy - new_entropy
        reward += entropy_gain

        # Penalize stagnation or increased uncertainty
        if entropy_gain <= 0:
            reward -= NO_PROGRESS_PENALTY

    # --------------------------------------------------
    # DISAGREEMENT (KL) REDUCTION BONUS
    # --------------------------------------------------
    prev_diag = prev_state.get("diagnostics", {})
    new_diag = new_state.get("diagnostics", {})

    prev_kl = prev_diag.get("disagreement_kl")
    new_kl = new_diag.get("disagreement_kl")

    if prev_kl is not None and new_kl is not None:
        kl_gain = prev_kl - new_kl
        reward += KL_BONUS_WEIGHT * kl_gain

    # --------------------------------------------------
    # REDUNDANCY / FATIGUE PENALTY
    # --------------------------------------------------
    # Penalize each additional question/action
    reward -= STEP_PENALTY

    # --------------------------------------------------
    # TERMINATION INCENTIVE (OPTIONAL, SAFE)
    # --------------------------------------------------
    if done:
        # Small positive bias for successful completion
        reward += 0.1

    return float(reward)
