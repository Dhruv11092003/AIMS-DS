import numpy as np

MAX_QUESTIONS = 5

def build_rl_state(session: dict) -> np.ndarray:
    """
    Builds RL state vector from session data.

    State:
    [avg_confidence,
     last_confidence,
     mcq_score,
     num_questions_norm,
     confidence_delta]
    """

    questions = session.get("questions", [])

    if not questions:
        return np.zeros(5, dtype=np.float32)

    confidences = [
        q["fusion_output"]["behavioral_confidence"]
        for q in questions
    ]

    avg_conf = float(np.mean(confidences))
    last_conf = float(confidences[-1])

    delta_conf = (
        confidences[-1] - confidences[-2]
        if len(confidences) > 1 else 0.0
    )

    mcq_score = session.get("mcq_result", {}).get("mcq_score", 0.0)

    num_q_norm = min(len(confidences) / MAX_QUESTIONS, 1.0)

    return np.array([
        avg_conf,
        last_conf,
        mcq_score,
        num_q_norm,
        delta_conf
    ], dtype=np.float32)
