"""
full_assessment.py
==================
End-to-end assessment API:
- Accepts video + MCQs
- Extracts audio, video, transcript
- Extracts features
- Runs fusion model
- Integrates MCQs
- Returns final decision
"""

import json
import uuid
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.media.video_service import save_video_for_inference
from app.services.transcript.transcript_service import generate_transcript_text

from app.services.features.audio_feature_service import extract_audio_features
from app.services.features.video_features import extract_video_features
from app.services.features.text_embedding_service import embed_text

from app.services.scoring.runtime_feature_builder import build_feature_vector
from app.services.scoring.fusion_inference_service import run_fusion_inference
from app.services.scoring.final_decision_service import compute_final_decision

router = APIRouter()

@router.post("/full-assessment")
async def full_assessment(
    video: UploadFile = File(...),
    mcq_answers: str = Form(...)
):
    """
    mcq_answers must be a JSON string.
    """

    try:
        # --------------------------------------------------
        # STEP 1: SAVE VIDEO + EXTRACT AUDIO (STATELESS)
        # --------------------------------------------------
        session_id = str(uuid.uuid4())

        media = save_video_for_inference(video)
        video_path = media["video_path"]
        audio_path = media["audio_path"]

        # --------------------------------------------------
        # STEP 2: TRANSCRIPTION (STATELESS)
        # --------------------------------------------------
        transcript = generate_transcript_text(audio_path)

        # --------------------------------------------------
        # STEP 3: FEATURE EXTRACTION
        # --------------------------------------------------
        audio_features = extract_audio_features(audio_path)

        video_feats = extract_video_features(video_path)
        fkps_features = video_feats["fkps"]
        gaze_features = video_feats["gaze"]
        pose_features = video_feats["pose"]

        text_features = embed_text(transcript)

        # --------------------------------------------------
        # STEP 4: FUSION INFERENCE
        # --------------------------------------------------
        feature_vector = build_feature_vector(
            audio_features=audio_features,
            fkps=fkps_features,
            gaze=gaze_features,
            pose=pose_features,
            text_embedding=text_features
        )

        fusion_output = run_fusion_inference(feature_vector)

        # --------------------------------------------------
        # STEP 5: FINAL DECISION (MCQ + FUSION)
        # --------------------------------------------------
        pseudo_session = {
            "questions": [{"question_id": 0, "fusion_output": fusion_output}],
            "mcq_answers": json.loads(mcq_answers)
        }
        final_result = compute_final_decision(pseudo_session)

        return {
            "session_id": session_id,
            "transcript": transcript,
            "result": final_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
