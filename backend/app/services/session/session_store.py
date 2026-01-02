"""
session_store.py
================
MongoDB-backed session store.
"""

from datetime import datetime
from app.core.database import session_collection
import uuid

def create_session(username: str) -> str:
    session_id = str(uuid.uuid4())

    session_collection.insert_one({
        "session_id": session_id,
        "username": username,
        "created_at": datetime.utcnow(),

        # -------------------------
        # VIDEO QUESTION STATE
        # -------------------------
        "questions": [],               # stores video question results

        # -------------------------
        # MCQ STATE (CRITICAL FIX)
        # -------------------------
        "mcq_answers": {},             # {question_id: selected_option}
        "asked_mcqs": [],              # ✅ TRACK already asked MCQs
        "mcq_score": 0.0,              # cumulative MCQ score

        # -------------------------
        # RL / ADAPTIVE STATE
        # -------------------------
        "rl_active": False,             # RL triggered or not
        "rl_steps": 0,                 # number of adaptive steps taken
        "confidence_history": [],      # behavioral confidence over time

        # -------------------------
        # FINAL OUTPUT
        # -------------------------
        "mcq_result": None,
        "session_result": None
    })

    return session_id

def get_session(session_id: str) -> dict:
    session = session_collection.find_one({"session_id": session_id})
    if not session:
        raise ValueError("Session not found")
    return serialize_session(session)


def store_mcq_answers(session_id: str, mcq_answers: dict, mcq_result: dict):
    session_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "mcq_answers": mcq_answers,
                "mcq_result": mcq_result
            }
        }
    )

def serialize_session(session: dict) -> dict:
    """
    Convert MongoDB session document to JSON-safe dict.
    """
    session = dict(session)

    # Remove MongoDB internal ID
    session.pop("_id", None)

    return session


def add_question_result(session_id: str, question_data: dict):
    session_collection.update_one(
        {"session_id": session_id},
        {"$push": {"questions": question_data}}
    )

def finalize_session(session_id: str, result: dict):
    session_collection.update_one(
        {"session_id": session_id},
        {"$set": {"session_result": result}}
    )
