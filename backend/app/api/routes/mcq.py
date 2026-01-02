"""
mcq.py
======
MCQ question fetch + submission APIs.
"""

import json
from fastapi import APIRouter, HTTPException, Form

from app.services.mcq.mcq_scoring_service import compute_mcq_score
from app.services.mcq.question_bank import MCQ_QUESTIONS, MCQ_OPTIONS
from app.services.session.session_store import store_mcq_answers
from app.services.session.session_store import get_session
from app.core.database import session_collection
router = APIRouter()

# --------------------------------------------------
# FETCH MCQ QUESTIONS (NEW)
# --------------------------------------------------

@router.get("/questions")
def get_mcq_questions():
    """
    Fetch static MCQ questions and options.
    """
    return {
        "questions": MCQ_QUESTIONS,
        "options": MCQ_OPTIONS
    }

# --------------------------------------------------
# SUBMIT MCQ ANSWERS (SESSION-LEVEL)
# --------------------------------------------------

@router.post("/{session_id}/mcq/submit")
def submit_mcq(session_id: str, mcq_answers: str = Form(...)):
    try:
        # ----------------------------
        # LOAD SESSION
        # ----------------------------
        session = get_session(session_id)

        # ----------------------------
        # PARSE INPUT (UNCHANGED)
        # ----------------------------
        # Example mcq_answers:
        # {"601": 2, "602": 1}
        mcq_answers_dict = json.loads(mcq_answers)

        # ----------------------------
        # PREVENT DUPLICATES
        # ----------------------------
        already_asked = set(session.get("asked_mcqs", []))
        new_question_ids = [
            int(qid) for qid in mcq_answers_dict.keys()
            if int(qid) not in already_asked
        ]

        if not new_question_ids:
            raise HTTPException(
                status_code=400,
                detail="All submitted MCQs were already answered"
            )

        # ----------------------------
        # SCORE MCQs (UNCHANGED LOGIC)
        # ----------------------------
        score_result = compute_mcq_score(mcq_answers_dict)

        # ----------------------------
        # UPDATE SESSION (RL-SAFE)
        # ----------------------------
        session_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                # Store answers
                **{
                    f"mcq_answers.{qid}": mcq_answers_dict[str(qid)]
                    for qid in new_question_ids
                },

                # ✅ THIS IS THE CRITICAL FIX
                "mcq_result": score_result
            },
            "$push": {
                "asked_mcqs": {"$each": new_question_ids}
            },
            "$inc": {
                "mcq_score": float(score_result["mcq_score"])
            }
        }
    )

        return score_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
