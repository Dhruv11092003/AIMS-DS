from fastapi import APIRouter, HTTPException
from app.services.features.audio_feature_service import process_audio_features

router = APIRouter(prefix="/features/audio", tags=["Audio Features"])


@router.post("/extract")
def extract_features(session_id: str, audio_path: str):
    try:
        features = process_audio_features(session_id, audio_path)
        return {
            "message": "Audio features extracted successfully",
            "features": features
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
