"""
transcript_service.py
=====================
Transcript generation using Whisper.

Supports:
- Session-based transcript storage (existing behavior)
- Stateless inference transcript generation (NEW)
"""

import whisper
import os
from datetime import datetime
from bson import ObjectId

from app.core.config import BACKEND_DIR
from app.core.database import session_collection

# ======================================================
# LOAD MODEL ONCE
# ======================================================

model = whisper.load_model("base")

# ======================================================
# PATH RESOLUTION
# ======================================================

def resolve_audio_path(audio_path: str) -> str:
    audio_path = audio_path.replace("\\", "/")
    abs_path = os.path.normpath(os.path.join(BACKEND_DIR, audio_path))

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Audio file not found at: {abs_path}")

    return abs_path

# ======================================================
# EXISTING SESSION-BASED TRANSCRIPTION (UNCHANGED)
# ======================================================

def generate_transcript(session_id: str, question_id: str, audio_path: str):
    audio_path = resolve_audio_path(audio_path)

    result = model.transcribe(audio_path)
    transcript_text = result["text"].strip()

    transcript_dir = "storage/transcripts"
    os.makedirs(transcript_dir, exist_ok=True)

    filename = f"{session_id}_{question_id}.txt"
    transcript_path = os.path.join(transcript_dir, filename)

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    session_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {
            "transcripts": {
                "question_id": question_id,
                "audio_path": audio_path,
                "transcript": transcript_text,
                "transcript_path": transcript_path,
                "generated_at": datetime.utcnow()
            }
        }}
    )

    return {
        "question_id": question_id,
        "transcript": transcript_text,
        "transcript_path": transcript_path
    }

# ======================================================
# NEW: STATELESS TRANSCRIPTION FOR INFERENCE (REQUIRED)
# ======================================================

def generate_transcript_text(audio_path: str) -> str:
    """
    Stateless transcript generation.
    Used for real-time inference (NO DB, NO SESSION).
    """

    if not os.path.isabs(audio_path):
        audio_path = os.path.abspath(audio_path)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    result = model.transcribe(audio_path)
    return result["text"].strip()
