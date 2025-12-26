from fastapi import APIRouter
from app.api.routes import session, media, transcript, audio_features, text_features, scoring, mcq




api_router = APIRouter()

api_router.include_router(session.router)
api_router.include_router(media.router)
api_router.include_router(transcript.router)
api_router.include_router(audio_features.router)
api_router.include_router(text_features.router)
api_router.include_router(scoring.router)
api_router.include_router(mcq.router)
