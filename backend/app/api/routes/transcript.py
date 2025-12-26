from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.core.database import session_collection
from app.services.transcript.transcript_service import generate_transcript

router = APIRouter(prefix="/transcript", tags=["Transcript"])


@router.post("/generate")
def generate_question_transcript(session_id: str, question_id: str):
    try:
        session = session_collection.find_one({"_id": ObjectId(session_id)})
        if not session:
            raise ValueError("Session not found")

        videos = session.get("videos", [])
        audio_path = None

        for v in videos:
            if v["question_id"] == question_id:
                audio_path = v.get("audio_path")
                break

        if not audio_path:
            raise ValueError("Audio not found for given question")

        transcript = generate_transcript(
            session_id=session_id,
            question_id=question_id,
            audio_path=audio_path
        )

        return {
            "message": "Transcript generated successfully",
            "result": transcript
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
