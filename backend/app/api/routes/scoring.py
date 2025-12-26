from fastapi import APIRouter, HTTPException
from app.services.scoring.confidence_service import compute_and_store_confidence

router = APIRouter(prefix="/confidence", tags=["Confidence Scoring"])


@router.post("/compute")
def compute_confidence(session_id: str):
    try:
        confidence = compute_and_store_confidence(session_id)
        return {
            "message": "Confidence score computed successfully",
            "confidence": confidence
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
