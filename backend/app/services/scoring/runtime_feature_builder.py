"""
runtime_feature_builder.py
==========================
FINAL runtime fusion builder.

Guarantees:
- Output vector ALWAYS matches training dimension (2288)
- No dependency on MediaPipe feature sizes
- Stable deployment behavior
"""

import numpy as np

# 🔒 LOCKED TRAINING DIMENSION
FUSION_DIM = 2288


def temporal_pool(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)

    if x.ndim == 1:
        return x

    mean = x.mean(axis=0)
    std = x.std(axis=0)

    return np.concatenate([mean.flatten(), std.flatten()])


def build_feature_vector(
    audio_features: np.ndarray,
    fkps: np.ndarray,
    gaze: np.ndarray,
    pose: np.ndarray,
    text_embedding: np.ndarray
) -> np.ndarray:
    """
    Build fusion vector and enforce fixed dimension.
    """

    audio_vec = temporal_pool(audio_features)
    fkps_vec = temporal_pool(fkps)
    gaze_vec = temporal_pool(gaze)
    pose_vec = temporal_pool(pose)
    text_vec = np.asarray(text_embedding, dtype=np.float32).flatten()

    fusion_vector = np.concatenate(
        [audio_vec, fkps_vec, gaze_vec, pose_vec, text_vec],
        axis=0
    ).astype(np.float32)

    # --------------------------------------------------
    # 🔒 ENFORCE FIXED DIMENSION (CRITICAL)
    # --------------------------------------------------
    cur_dim = fusion_vector.shape[0]

    if cur_dim > FUSION_DIM:
        fusion_vector = fusion_vector[:FUSION_DIM]

    elif cur_dim < FUSION_DIM:
        pad_width = FUSION_DIM - cur_dim
        fusion_vector = np.pad(
            fusion_vector,
            (0, pad_width),
            mode="constant",
            constant_values=0.0
        )

    return fusion_vector
