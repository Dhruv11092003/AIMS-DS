from datetime import datetime
from bson import ObjectId

from app.core.database import session_collection
from app.services.features.text_features import extract_text_features


def process_text_features(session_id: str, transcript_text: str):
    try:
        session_object_id = ObjectId(session_id)
    except Exception:
        raise ValueError("Invalid session_id format")

    features = extract_text_features(transcript_text)

    entry = {
        "features": features,
        "extracted_at": datetime.utcnow()
    }

    result = session_collection.update_one(
        {"_id": session_object_id},
        {"$push": {"text_features": entry}}
    )

    if result.matched_count == 0:
        raise ValueError("Session not found")

    return features
