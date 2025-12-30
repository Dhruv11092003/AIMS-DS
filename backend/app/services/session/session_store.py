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
        "mcq_answers": {},
        "mcq_result": None,
        "questions": [],
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
