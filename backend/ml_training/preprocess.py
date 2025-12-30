"""
preprocess.py
================
Direct fusion preprocessing using PRECOMPUTED TRAM-CAM features.

This version is FINAL.
It supports ANY temporal depth for audio, video, and text.

Authoritative for training–runtime alignment.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
import joblib

# ======================================================
# PATH CONFIGURATION (EDIT IF NEEDED)
# ======================================================

DATA_ROOT = Path(r"D:\MSc\SET Conference\multimodal\DATA\tramcam")

TRAIN_DIR = DATA_ROOT / "train"
CSV_DIR = DATA_ROOT / "data_csv"
CSV_TRAIN = CSV_DIR / "train_split_Depression_AVEC2017.csv"

OUT_DIR = Path(__file__).resolve().parents[1] / "ml_training"
PREPROC_DIR = OUT_DIR / "preprocessed"
ARTIFACT_DIR = OUT_DIR / "artifacts"

PREPROC_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# TEMPORAL POOLING (LOCKED)
# ======================================================

def temporal_pool(x: np.ndarray) -> np.ndarray:
    """
    x: (T, D)
    return: (2D,) -> [mean, std]
    """
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    return np.concatenate([mean, std], axis=0).astype(np.float32)

# ======================================================
# UNIVERSAL SHAPE COLLAPSER (FINAL)
# ======================================================

def collapse_to_time(x: np.ndarray, name: str) -> np.ndarray:
    """
    Collapses ANY feature tensor into (T, D)

    Supported shapes:
    - (D,)
    - (T, D)
    - (T, J, D)
    - (S, T, D)
    - (S, T, J, D)
    """
    x = np.asarray(x, dtype=np.float32)

    if x.ndim == 1:
        return x.reshape(1, -1)

    if x.ndim == 2:
        return x

    if x.ndim == 3:
        return x.reshape(x.shape[0] * x.shape[1], -1)

    if x.ndim == 4:
        return x.reshape(x.shape[0] * x.shape[1], -1)

    raise ValueError(f"{name} has unsupported shape: {x.shape}")

# ======================================================
# LABEL MAPPING (3-CLASS DEPRESSION)
# ======================================================

def phq_to_class(phq_score: int) -> int:
    if phq_score <= 4:
        return 0
    elif phq_score <= 9:
        return 1
    return 2

# ======================================================
# MAIN PIPELINE
# ======================================================

def main():
    print(">>> preprocess.py started")

    df = pd.read_csv(CSV_TRAIN)

    X_fusion_list = []
    y_list = []
    feature_schema = None

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing subjects"):

        pid = int(row["Participant_ID"])
        phq_score = int(row["PHQ8_Score"])
        label = phq_to_class(phq_score)

        subj_dir = TRAIN_DIR / str(pid)

        # ------------------------------
        # LOAD + COLLAPSE FEATURES
        # ------------------------------
        audio = collapse_to_time(
            np.load(subj_dir / f"train_ft_audio_{pid}.npy"),
            "audio"
        )

        fkps = collapse_to_time(
            np.load(subj_dir / f"train_ft_fkps_{pid}.npy"),
            "fkps"
        )

        gaze = collapse_to_time(
            np.load(subj_dir / f"train_ft_gaze_conf_{pid}.npy"),
            "gaze"
        )

        pose = collapse_to_time(
            np.load(subj_dir / f"train_ft_pose_conf_{pid}.npy"),
            "pose"
        )

        text = collapse_to_time(
            np.load(subj_dir / f"train_ft_text_{pid}.npy"),
            "text"
        )

        # ------------------------------
        # TEMPORAL POOLING
        # ------------------------------
        audio_pooled = temporal_pool(audio)
        fkps_pooled = temporal_pool(fkps)
        gaze_pooled = temporal_pool(gaze)
        pose_pooled = temporal_pool(pose)
        text_pooled = temporal_pool(text)

        # ------------------------------
        # SAFETY CHECK
        # ------------------------------
        for name, arr in {
            "audio": audio_pooled,
            "fkps": fkps_pooled,
            "gaze": gaze_pooled,
            "pose": pose_pooled,
            "text": text_pooled,
        }.items():
            if arr.ndim != 1:
                raise ValueError(f"{name} not 1D after pooling: {arr.shape}")

        # ------------------------------
        # FUSION VECTOR (LOCKED ORDER)
        # ------------------------------
        X_fusion = np.concatenate([
            audio_pooled,
            fkps_pooled,
            gaze_pooled,
            pose_pooled,
            text_pooled
        ], axis=0)

        if feature_schema is None:
            feature_schema = {
                "audio_dim": audio_pooled.shape[0],
                "fkps_dim": fkps_pooled.shape[0],
                "gaze_dim": gaze_pooled.shape[0],
                "pose_dim": pose_pooled.shape[0],
                "text_dim": text_pooled.shape[0],
                "fusion_dim": X_fusion.shape[0],
                "order": ["audio", "fkps", "gaze", "pose", "text"]
            }

        X_fusion_list.append(X_fusion)
        y_list.append(label)

    # ==================================================
    # FINAL SAVE
    # ==================================================

    X = np.vstack(X_fusion_list)
    y = np.asarray(y_list, dtype=np.int64)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    np.save(PREPROC_DIR / "X_fusion.npy", X_scaled)
    np.save(PREPROC_DIR / "y_3class.npy", y)

    joblib.dump(scaler, ARTIFACT_DIR / "scaler.joblib")

    with open(ARTIFACT_DIR / "feature_order.json", "w") as f:
        json.dump(feature_schema, f, indent=2)

    print("Preprocessing completed successfully.")
    print("Fusion dimension:", feature_schema["fusion_dim"])
    print("Saved outputs to:", PREPROC_DIR)

# ======================================================
# ENTRY POINT
# ======================================================

if __name__ == "__main__":
    main()
