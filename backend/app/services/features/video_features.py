"""
video_features.py
=================
Video feature extraction service.

Extracts:
- Facial keypoints (fkps)
- Gaze proxy features
- Pose proxy features

Uses MediaPipe Face Mesh.
Output shapes are compatible with fusion training pipeline.
"""

import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

# ======================================================
# MEDIAPIPE INITIALIZATION
# ======================================================

mp_face_mesh = mp.solutions.face_mesh

FACE_MESH = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ======================================================
# CONSTANTS
# ======================================================

# MediaPipe face mesh has 468 landmarks
# We select 68 stable landmarks (mouth, eyes, eyebrows, nose)

SELECTED_LANDMARKS = [
    33, 133, 362, 263,     # eyes
    1, 2, 98, 327,         # nose
    61, 291, 78, 308,      # mouth
    70, 63, 105, 66,       # eyebrows
    336, 296, 334, 293
]

# Ensure exactly 68 indices (repeat if needed)
while len(SELECTED_LANDMARKS) < 68:
    SELECTED_LANDMARKS.append(SELECTED_LANDMARKS[-1])

# ======================================================
# MAIN EXTRACTION FUNCTION
# ======================================================

def extract_video_features(video_path: str) -> dict:
    """
    Extracts video features from a video file.

    Args:
        video_path (str): Path to video file

    Returns:
        {
            "fkps": np.ndarray,   # (T, 68, 4)
            "gaze": np.ndarray,   # (T, 4)
            "pose": np.ndarray    # (T, 2)
        }
    """

    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(video_path))

    fkps_frames = []
    gaze_frames = []
    pose_frames = []

    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = FACE_MESH.process(rgb_frame)

        if not results.multi_face_landmarks:
            continue

        landmarks = results.multi_face_landmarks[0].landmark

        # --------------------------------------------------
        # FACIAL KEYPOINTS (68 × 4)
        # --------------------------------------------------
        fkps = []
        for idx in SELECTED_LANDMARKS:
            lm = landmarks[idx]
            fkps.append([
                lm.x,
                lm.y,
                lm.z,
                lm.visibility if hasattr(lm, "visibility") else 1.0
            ])

        fkps = np.array(fkps, dtype=np.float32)  # (68, 4)

        # --------------------------------------------------
        # GAZE PROXY (4)
        # Simple proxy: eye center movement
        # --------------------------------------------------
        left_eye = np.mean(fkps[0:2, :2], axis=0)
        right_eye = np.mean(fkps[2:4, :2], axis=0)

        gaze = np.concatenate([
            left_eye,
            right_eye
        ], axis=0)  # (4,)

        # --------------------------------------------------
        # POSE PROXY (2)
        # Simple proxy: nose tip movement
        # --------------------------------------------------
        nose = fkps[4, :2]  # (x, y)

        pose = nose  # (2,)

        fkps_frames.append(fkps)
        gaze_frames.append(gaze)
        pose_frames.append(pose)

    cap.release()

    if len(fkps_frames) == 0:
        raise RuntimeError("No facial landmarks detected in video.")

    # ------------------------------------------------------
    # STACK TEMPORAL DIMENSION
    # ------------------------------------------------------

    fkps_arr = np.stack(fkps_frames, axis=0)    # (T, 68, 4)
    gaze_arr = np.stack(gaze_frames, axis=0)    # (T, 4)
    pose_arr = np.stack(pose_frames, axis=0)    # (T, 2)

    return {
        "fkps": fkps_arr,
        "gaze": gaze_arr,
        "pose": pose_arr
    }
