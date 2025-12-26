from fastapi import APIRouter,HTTPException
from app.services.mcq.question_bank import MCQ_QUESTIONS
from app.services.mcq.mcq_evaluator import evaluate_mcq


router = APIRouter(prefix="/mcq", tags=["MCQ"])

@router.get("/questions")
def get_mcq_questions():
    return {
        "questions": MCQ_QUESTIONS
    }


@router.post("/submit")
def submit_mcq(session_id: str, answers: dict):
    try:
        result = evaluate_mcq(session_id, answers)
        return {
            "message": "MCQ submitted successfully",
            "result": result
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid MCQ submission")
