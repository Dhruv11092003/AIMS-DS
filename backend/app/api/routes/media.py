from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.media.video_service import handle_video_upload

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload-video")
def upload_video(
    session_id: str = Form(...),
    question_id: str = Form(...),
    video: UploadFile = File(...)
):
    try:
        paths = handle_video_upload(session_id, question_id, video)
        return {
            "message": "Video and audio processed successfully",
            "video_path": paths["video_path"],
            "audio_path": paths["audio_path"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

