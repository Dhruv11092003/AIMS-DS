from fastapi import APIRouter, HTTPException
from app.services.features.text_feature_service import process_text_features

router = APIRouter(prefix="/features/text", tags=["Text Features"])


@router.post("/extract")
def extract_text_features_api(session_id: str, transcript: str):
    try:
        features = process_text_features(session_id, transcript)
        return {
            "message": "Text features extracted successfully",
            "features": features
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
