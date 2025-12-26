import whisper
import os
from datetime import datetime
from bson import ObjectId
from app.core.config import BACKEND_DIR
from app.core.database import session_collection


# Load model once (important)
model = whisper.load_model("base")

def resolve_audio_path(audio_path: str) -> str:
    """
    Convert stored relative path into absolute, OS-safe path
    """
    # Normalize slashes first
    audio_path = audio_path.replace("\\", "/")

    # Make absolute from backend root
    abs_path = os.path.normpath(os.path.join(BACKEND_DIR, audio_path))

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Audio file not found at: {abs_path}")

    return abs_path


def generate_transcript(session_id: str, question_id: str, audio_path: str):
    # 🔥 FIX: Resolve absolute path
    if not os.path.isabs(audio_path):
        audio_path = os.path.abspath(audio_path)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at path: {audio_path}")

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




