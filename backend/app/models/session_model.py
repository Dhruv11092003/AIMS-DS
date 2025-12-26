from datetime import datetime
from typing import Dict, Any


def create_session_document(user_id: str | None = None) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "status": "active",
        "current_stage": "video",
        "video_scores": {},
        "mcq_scores": {},
        "final_score": None,
        "rl_state": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
