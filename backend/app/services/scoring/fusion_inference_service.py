"""
fusion_inference_service.py
===========================
FINAL runtime inference service for DIRECT multimodal fusion.

ASSUMPTIONS (LOCKED):
- Model is trained on ALREADY fused feature vectors
- No scalers, no PCA, no schema files
- Feature pooling + concatenation happens BEFORE this service
- This service receives EXACTLY ONE fused feature vector

This file MUST NOT perform:
- feature extraction
- temporal pooling
- scaling
- modality handling
"""

import numpy as np
import joblib
from pathlib import Path

# ======================================================
# LOAD TRAINED FUSION MODEL
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[4]
MODEL_PATH = BASE_DIR / "backend" / "ml_training" / "models" / "fusion_model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Fusion model not found at: {MODEL_PATH}")

MODEL = joblib.load(MODEL_PATH)

# ======================================================
# MAIN INFERENCE FUNCTION (FINAL CONTRACT)
# ======================================================

def run_fusion_inference(feature_vector: np.ndarray) -> dict:
    """
    Run inference on a single fused feature vector.

    Args:
        feature_vector (np.ndarray):
            Shape: (D,) or (1, D)
            D must match training fusion dimension (e.g., 2288)

    Returns:
        {
            "predicted_class": str,
            "class_probabilities": dict,
            "behavioral_confidence": float
        }
    """

    # ------------------------------
    # SANITY CHECK + RESHAPE
    # ------------------------------
    feature_vector = np.asarray(feature_vector, dtype=np.float32)

    if feature_vector.ndim == 1:
        feature_vector = feature_vector.reshape(1, -1)
    elif feature_vector.ndim != 2 or feature_vector.shape[0] != 1:
        raise ValueError(
            f"Invalid feature_vector shape: {feature_vector.shape}. "
            f"Expected (D,) or (1, D)."
        )

    # ------------------------------
    # MODEL INFERENCE
    # ------------------------------
    probs = MODEL.predict_proba(feature_vector)[0]
    pred_idx = int(np.argmax(probs))

    class_labels = ["Low", "Moderate", "High"]

    sorted_probs = np.sort(probs)[::-1]
    behavioral_confidence = float(sorted_probs[0] - sorted_probs[1])

    # ------------------------------
    # OUTPUT
    # ------------------------------
    return {
        "predicted_class": class_labels[pred_idx],
        "class_probabilities": {
            class_labels[i]: float(probs[i])
            for i in range(len(class_labels))
        },
        "behavioral_confidence": behavioral_confidence
    }
