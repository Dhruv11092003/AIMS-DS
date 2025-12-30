import numpy as np
from sentence_transformers import SentenceTransformer

# Load model once
_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text_features(text: str) -> np.ndarray:
    """
    Extract text embedding as a numeric vector.

    Output shape: (D,)
    """
    embedding = _MODEL.encode(text)

    return np.asarray(embedding, dtype=np.float32)
