"""
video_service.py
================
Video handling utilities.

Supports:
- Session-based upload & storage (existing)
- Stateless video handling for inference (NEW)
"""

from datetime import datetime
from bson import ObjectId
from pathlib import Path

from app.utils.file_utils import save_uploaded_file
from app.core.database import session_collection
from app.services.media.audio_service import extract_audio_from_video

VIDEO_UPLOAD_DIR = "storage/videos"

# ======================================================
# EXISTING SESSION-BASED VIDEO HANDLING (UNCHANGED)
# ======================================================

def handle_video_upload(session_id: str, question_id: str, video_file):
    try:
        session_object_id = ObjectId(session_id)
    except Exception:
        raise ValueError("Invalid session_id format")

    video_path = save_uploaded_file(VIDEO_UPLOAD_DIR, video_file)
    audio_path = extract_audio_from_video(video_path)

    video_entry = {
        "question_id": question_id,
        "video_path": video_path,
        "audio_path": audio_path,
        "uploaded_at": datetime.utcnow()
    }

    result = session_collection.update_one(
        {"_id": session_object_id},
        {"$push": {"videos": video_entry}}
    )

    if result.matched_count == 0:
        raise ValueError("Session not found")

    return {
        "video_path": video_path,
        "audio_path": audio_path
    }

# ======================================================
# NEW: STATELESS VIDEO HANDLING FOR INFERENCE (REQUIRED)
# ======================================================

def save_video_for_inference(video_file) -> dict:
    """
    Save uploaded video and extract audio.
    No DB, no session dependency.
    """

    video_path = save_uploaded_file(VIDEO_UPLOAD_DIR, video_file)
    audio_path = extract_audio_from_video(video_path)

    return {
        "video_path": video_path,
        "audio_path": audio_path
    }
