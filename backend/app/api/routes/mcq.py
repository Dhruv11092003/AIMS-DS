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
        mcq_answers_dict = json.loads(mcq_answers)
        mcq_result = compute_mcq_score(mcq_answers_dict)

        store_mcq_answers(
            session_id=session_id,
            mcq_answers=mcq_answers_dict,
            mcq_result=mcq_result
        )

        return mcq_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
