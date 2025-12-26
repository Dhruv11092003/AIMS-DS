from datetime import datetime
from bson import ObjectId
from app.core.database import session_collection
from app.services.mcq.question_bank import MCQ_QUESTIONS


def evaluate_mcq(session_id: str, answers: dict):
    total_score = 0

    for q in MCQ_QUESTIONS:
        qid = q["question_id"]
        selected = answers.get(qid)

        for opt in q["options"]:
            if opt["option_id"] == selected:
                total_score += opt["score"]

    mcq_entry = {
        "answers": answers,
        "total_score": total_score,
        "submitted_at": datetime.utcnow()
    }

    session_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"mcq_responses": mcq_entry}}
    )

    return {
        "mcq_score": total_score
    }
