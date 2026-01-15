from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title="AIMS-DS",
        description="Adaptive Interview Monitoring System for Depression Screening",
        version="1.0.0"
    )

    # CORS configuration (frontend will connect later)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include all API routes
    app.include_router(api_router)

    return app


app = create_application()


@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {
        "project": "AIMS-DS",
        "status": "Backend is running",
        "message": "Adaptive Interview Monitoring System for Depression Screening"
    }
