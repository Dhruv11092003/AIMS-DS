from datetime import datetime
from bson import ObjectId
from app.core.database import session_collection
from app.services.scoring.fusion_engine import compute_overall_confidence

def compute_and_store_confidence(session_id: str):
    session = session_collection.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise ValueError("Session not found")

    audio_features = session.get("audio_features", [])
    text_features = session.get("text_features", [])
    mcq_responses = session.get("mcq_responses", [])

    if not audio_features or not text_features or not mcq_responses:
        raise ValueError("Insufficient data for confidence computation")

    latest_audio = audio_features[-1]["features"]
    latest_text = text_features[-1]["features"]
    mcq_score = mcq_responses[-1]["total_score"]

    confidence = compute_overall_confidence(
        latest_audio,
        latest_text,
        mcq_score
    )

    session_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "confidence": confidence
        }}
    )

    return confidence

