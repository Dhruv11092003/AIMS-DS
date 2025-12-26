from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime
