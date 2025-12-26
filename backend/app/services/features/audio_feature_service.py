from datetime import datetime
from bson import ObjectId

from app.core.database import session_collection
from app.services.features.audio_features import extract_audio_features


def process_audio_features(session_id: str, audio_path: str):
    try:
        session_object_id = ObjectId(session_id)
    except Exception:
        raise ValueError("Invalid session_id format")

    features = extract_audio_features(audio_path)

    feature_entry = {
        "audio_path": audio_path,
        "features": features,
        "extracted_at": datetime.utcnow()
    }

    result = session_collection.update_one(
        {"_id": session_object_id},
        {"$push": {"audio_features": feature_entry}}
    )

    if result.matched_count == 0:
        raise ValueError("Session not found")

    return features
