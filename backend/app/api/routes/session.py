from fastapi import APIRouter
from datetime import datetime

from app.schemas.session_schema import SessionCreate, SessionResponse
from app.services.session_service import start_session

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/start", response_model=SessionResponse)
def start_new_session(payload: SessionCreate):
    session_id = start_session(payload.user_id)

    return SessionResponse(
        session_id=session_id,
        status="active",
        created_at=datetime.utcnow()
    )
