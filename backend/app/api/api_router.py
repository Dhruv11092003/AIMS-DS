from fastapi import APIRouter
from app.api.routes import session, media

api_router = APIRouter()

api_router.include_router(session.router)
api_router.include_router(media.router)
