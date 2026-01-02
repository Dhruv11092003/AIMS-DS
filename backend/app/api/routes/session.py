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
from app.core.database import session_collection
from app.services.scoring.fusion_inference_service import run_fusion_inference
from app.services.session.question_selector import (
    select_baseline_video_question,
    select_rl_video_question,
    
)
from app.services.mcq.mcq_selector import select_rl_mcq
from app.services.rl.rl_state_builder import build_rl_state
from app.services.rl.rl_policy_loader import get_rl_policy
from app.services.rl.rl_action_mapper import map_action



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

        session_collection.update_one(
            {"session_id": session_id},
            {
                "$push": {
                    "confidence_history": fusion_output["behavioral_confidence"]
                    }
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
    

    
@router.get("/{session_id}/next-question")
def get_next_question(session_id: str):
    session = get_session(session_id)

    asked_video_ids = [
        q["question_id"] for q in session.get("questions", [])
    ]

    # ======================================================
    # STEP 1 — BASELINE VIDEO QUESTIONS
    # ======================================================
    baseline_q = select_baseline_video_question(asked_video_ids)
    if baseline_q is not None:
        return {
            "type": "video",
            "question": baseline_q
        }

    # ======================================================
    # STEP 2 — BASELINE MCQs (ONCE)
    # ======================================================
    if session.get("mcq_result") is None:
        return {
            "type": "mcq",
            "mode": "baseline"
        }

    # ======================================================
    # STEP 3 — CONFIDENCE CHECK
    # ======================================================
    if not session.get("questions"):
        return {"type": "finalize"}

    confidences = [
        q["fusion_output"]["behavioral_confidence"]
        for q in session["questions"]
    ]

    max_conf = max(confidences)

    # ------------------------------
    # EARLY STOP IF CONFIDENT
    # ------------------------------
    if max_conf >= 0.65:
        return {"type": "finalize"}

    # ======================================================
    # STEP 4 — ACTIVATE RL (DB UPDATE)
    # ======================================================
    if not session.get("rl_active", False):
        session_collection.update_one(
            {"session_id": session_id},
            {"$set": {"rl_active": True}}
        )
        session["rl_active"] = True  # sync local copy

    # ======================================================
    # STEP 5 — RL DECISION
    # ======================================================
    state = build_rl_state(session)
    rl_model = get_rl_policy()
    action, _ = rl_model.predict(state, deterministic=True)

    decision = map_action(int(action))

    # ------------------------------------------------------
    # INCREMENT RL STEP COUNT (DB UPDATE)
    # ------------------------------------------------------
    session_collection.update_one(
        {"session_id": session_id},
        {"$inc": {"rl_steps": 1}}
    )

    # ======================================================
    # STEP 6 — MAP RL ACTION → QUESTION
    # ======================================================
    if decision["type"] == "video":
        q = select_rl_video_question(
            decision["difficulty"],
            asked_video_ids
        )

        if q is None:
            return {"type": "finalize"}

        return {
            "type": "video",
            "question": q
        }

    if decision["type"] == "mcq":
        mcq = select_rl_mcq(
            decision.get("difficulty", "medium"),
            session=session  # IMPORTANT for no repetition
        )

        if mcq is None:
            return {"type": "finalize"}

        return {
            "type": "mcq",
            "question": mcq
        }

    # ======================================================
    # STEP 7 — FINAL FALLBACK
    # ======================================================
    return {"type": "finalize"}
