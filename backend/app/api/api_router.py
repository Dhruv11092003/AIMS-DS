from fastapi import APIRouter
from app.api.routes import session, media, transcript, scoring, mcq
from app.api.routes.full_assessment import router as full_assessment_router #for testing not for prod
from app.api.routes.mcq import router as mcq_router
from app.api.routes.session import router as session_router
# from backend.app.api.routes import text_features_routes
# from backend.archive import audio_features
api_router = APIRouter()

api_router.include_router(session.router)
# api_router.include_router(media.router)
# api_router.include_router(transcript.router)
# api_router.include_router(audio_features.router)
# api_router.include_router(text_features_routes.router)
api_router.include_router(scoring.router)
# api_router.include_router(mcq.router)
api_router.include_router(
    full_assessment_router,
    prefix="/assessment",
    tags=["Full Assessment"]
)

api_router.include_router(
    mcq_router,
    prefix="/session",
    tags=["MCQ"]
)

api_router.include_router(
    session_router,
    prefix="/session",
    tags=["Session"]
)