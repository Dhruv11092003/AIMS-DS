"""
session.py
==========
Session-based orchestration APIs (video questions only).
"""

import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from app.services.session.session_store import (
    get_session,
    add_question_result,
    finalize_session,
    create_session,
)
from app.services.scoring.runtime_feature_builder import build_feature_vector

from app.services.media.video_service import save_video_for_inference
from app.services.transcript.transcript_service import generate_transcript_text
from app.services.scoring.final_decision_service import compute_final_decision
from app.services.features.audio_feature_service import extract_audio_features
from app.services.features.video_features import extract_video_features
from app.services.features.text_embedding_service import embed_text

from app.services.scoring.fusion_inference_service import run_fusion_inference

router = APIRouter()

@router.post("/create")
def create_new_session(username: str = Form(...)):
    """
    Create a new interview session with username.
    """
    if not username or not username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    session_id = create_session(username=username)

    return {
        "session_id": session_id,
        "username": username
    }
# --------------------------------------------------
# OPTIONAL: GET SESSION (DEBUGGING)
# --------------------------------------------------

@router.get("/{session_id}")
def get_session_details(session_id: str):
    try:
        session = get_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{session_id}/question/{question_id}/submit")
async def submit_question(
    session_id: str,
    question_id: int,
    video: UploadFile = File(...)
):
    try:
        media = save_video_for_inference(video)
        video_path = media["video_path"]
        audio_path = media["audio_path"]

        transcript = generate_transcript_text(audio_path)

        audio_features = extract_audio_features(audio_path)
        # video_features = extract_video_features(video_path)
        text_features = embed_text(transcript)



        video_feats = extract_video_features(video_path)

        fusion_vector = build_feature_vector(
            audio_features=audio_features,
            fkps=video_feats["fkps"],
            gaze=video_feats["gaze"],
            pose=video_feats["pose"],
            text_embedding=text_features
        )


        fusion_output = run_fusion_inference(fusion_vector)

        add_question_result(
            session_id,
            {
                "question_id": question_id,
                "video_path": video_path,
                "transcript": transcript,
                "fusion_output": fusion_output
            }
        )

        return {
            "question_id": question_id,
            "behavioral_confidence": fusion_output["behavioral_confidence"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/{session_id}/finalize")
def finalize(session_id: str):
    try:
        session = get_session(session_id)

        if not session["questions"]:
            raise ValueError("No questions submitted")

        if not session["mcq_result"]:
            raise ValueError("MCQs not submitted")

        behavioral_confidences = [
            q["fusion_output"]["behavioral_confidence"]
            for q in session["questions"]
        ]

        avg_behavioral_conf = sum(behavioral_confidences) / len(behavioral_confidences)

        # Fake fusion_output to reuse final_decision_service
        fusion_proxy = {
            "behavioral_confidence": avg_behavioral_conf,
            "class_probabilities": {},
            "predicted_class": None
        }

        final_result = compute_final_decision(
            fusion_output=fusion_proxy,
            mcq_answers=session["mcq_answers"]
        )

        finalize_session(session_id, final_result)

        return final_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))