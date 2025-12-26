from bson import ObjectId
from app.core.database import session_collection
from app.models.session_model import create_session_document


def start_session(user_id: str | None = None) -> str:
    """
    Create a new screening session and store it in MongoDB
    """
    session_doc = create_session_document(user_id)
    result = session_collection.insert_one(session_doc)
    return str(result.inserted_id)
