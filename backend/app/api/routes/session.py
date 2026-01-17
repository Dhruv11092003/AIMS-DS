"""
Session orchestration for AIMS-DS (STAGE 5 – FINAL HANDSHAKE).

This controller coordinates:
- Video question flow
- MCQ submission
- Bayesian final decision
- Entropy-based RL activation
- Safe termination and storage

Key Changes:
- Confidence threshold REMOVED
- Entropy / needs_rl_refinement drives control
- Bayesian posterior history stored
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import numpy as np
from app.services.mcq.question_bank import MCQ_QUESTIONS
from app.services.session.session_store import (
    get_session,
    create_session,
    add_question_result,
    finalize_session,
)
from app.core.database import session_collection

from app.services.media.video_service import save_video_for_inference
from app.services.transcript.transcript_service import generate_transcript_text
from app.services.features.audio_feature_service import extract_audio_features
from app.services.features.video_features import extract_video_features
from app.services.features.text_embedding_service import embed_text
from app.services.scoring.runtime_feature_builder import build_feature_vector
from app.services.scoring.fusion_inference_service import run_fusion_inference
from app.services.scoring.final_decision_service import compute_final_decision

from app.services.session.question_selector import select_baseline_video_question
from app.services.mcq.mcq_selector import select_rl_mcq

from app.services.rl.rl_state_builder import build_rl_state
from app.services.rl.rl_policy_loader import get_rl_policy
from app.services.rl.rl_action_mapper import map_action


# ======================================================
# CONFIGURATION
# ======================================================

MAX_BASELINE_QUESTIONS = 8
MAX_RL_STEPS = 5
ENTROPY_STAGNATION_EPS = 0.02  # minimal entropy improvement

router = APIRouter()


# ======================================================
# SESSION CREATION
# ======================================================

@router.post("/create")
def create_new_session(username: str = Form(...)):
    if not username or not username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    session_id = create_session(username=username)

    return {
        "session_id": session_id,
        "username": username
    }


# ======================================================
# DEBUG / INSPECTION
# ======================================================

@router.get("/{session_id}")
def get_session_details(session_id: str):
    try:
        return get_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ======================================================
# VIDEO QUESTION SUBMISSION
# ======================================================

@router.post("/{session_id}/question/{question_id}/submit")
async def submit_question(
    session_id: str,
    question_id: int,
    video: UploadFile = File(...)
):
    try:
        media = save_video_for_inference(video)
        transcript = generate_transcript_text(media["audio_path"])

        audio_features = extract_audio_features(media["audio_path"])
        video_features = extract_video_features(media["video_path"])
        text_features = embed_text(transcript)

        fusion_vector = build_feature_vector(
            audio_features=audio_features,
            fkps=video_features["fkps"],
            gaze=video_features["gaze"],
            pose=video_features["pose"],
            text_embedding=text_features
        )

        fusion_output = run_fusion_inference(fusion_vector)

        add_question_result(
            session_id,
            {
                "question_id": question_id,
                "video_path": media["video_path"],
                "transcript": transcript,
                "fusion_output": fusion_output
            }
        )

        # Store Bayesian history placeholder (filled after MCQs)
        session_collection.update_one(
            {"session_id": session_id},
            {"$push": {"fusion_history": fusion_output}}
        )

        return {
            "question_id": question_id,
            "behavioral_confidence": fusion_output["behavioral_confidence"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# NEXT QUESTION CONTROLLER (CORE HANDSHAKE)
# ======================================================

@router.get("/{session_id}/next-question")
@router.get("/{session_id}/next-question")
def get_next_question(session_id: str):
    session = get_session(session_id)

    # --------------------------------------------------
    # STEP 1 — VIDEO QUESTIONS
    # --------------------------------------------------
    asked_video_ids = [q["question_id"] for q in session.get("questions", [])]
    video_q = select_baseline_video_question(asked_video_ids)

    if video_q is not None:
        return {"type": "video", "question": video_q}

    # --------------------------------------------------
    # STEP 2 — BASELINE PHQ-8 (MANDATORY)
    # --------------------------------------------------
    mcq_answers = session.get("mcq_answers") or {}
    baseline_answered = len(mcq_answers)

    if baseline_answered < MAX_BASELINE_QUESTIONS:
        next_mcq = MCQ_QUESTIONS[baseline_answered]
        return {
            "type": "mcq",
            "mode": "baseline",
            "question": next_mcq
        }

    # --------------------------------------------------
    # STEP 3 — BAYESIAN DECISION (POST-BASELINE ONLY)
    # --------------------------------------------------
    final_decision = compute_final_decision(session)

    session_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {"final_decision": final_decision},
            "$push": {"posterior_history": final_decision["final_probabilities"]}
        }
    )
    session["final_decision"] = final_decision

    # --------------------------------------------------
    # STEP 4 — CHECK IF RL IS REQUIRED
    # --------------------------------------------------
    if not final_decision["needs_rl_refinement"]:
        return {"type": "finalize"}

    # --------------------------------------------------
    # STEP 5 — RL BUDGET CHECK
    # --------------------------------------------------
    rl_steps = session.get("rl_steps", 0)
    if rl_steps >= MAX_RL_STEPS:
        return {"type": "finalize"}

    # --------------------------------------------------
    # STEP 6 — RL HANDSHAKE
    # --------------------------------------------------
    state = build_rl_state(session)
    rl_model = get_rl_policy()
    action, _ = rl_model.predict(state, deterministic=True)
    decision = map_action(int(action))

    session_collection.update_one(
        {"session_id": session_id},
        {"$inc": {"rl_steps": 1}}
    )

    # --------------------------------------------------
    # STEP 7 — RL MCQ
    # --------------------------------------------------
    if decision.get("type") == "mcq":
        mcq = select_rl_mcq(
            decision.get("difficulty", "medium"),
            session=session
        )
        if mcq:
            return {"type": "mcq", "question": mcq}

    return {"type": "finalize"}


@router.post("/{session_id}/finalize")
def finalize(session_id: str):
    try:
        session = get_session(session_id)

        if not session.get("final_decision"):
            final_decision = compute_final_decision(session)
        else:
            final_decision = session["final_decision"]

        # Persist final calibrated result
        finalize_session(session_id, {
            "final_class": final_decision["final_class"],
            "final_probabilities": final_decision["final_probabilities"],
            "uncertainty_level": final_decision["uncertainty_level"],
            "behavioral_evidence": final_decision["diagnostics"]["behavioral_probabilities"],
            "psychometric_evidence": final_decision["diagnostics"]["psychometric_probabilities"],
            "posterior_history": session.get("posterior_history", [])
        })

        return final_decision

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
