"""
text_embedding_service.py
=========================
Runtime text embedding service.

- Uses pretrained SentenceTransformer
- Outputs 768-D embeddings
- Compatible with TRAM-CAM precomputed text features
- Safe for production inference
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# ======================================================
# LOAD MODEL ONCE (GLOBAL)
# ======================================================

_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

try:
    _model = SentenceTransformer(_MODEL_NAME)
except Exception as e:
    raise RuntimeError(
        f"Failed to load text embedding model '{_MODEL_NAME}': {e}"
    )

# ======================================================
# MAIN EMBEDDING FUNCTION
# ======================================================

def embed_text(text: str) -> np.ndarray:
    """
    Convert transcript text into embedding.

    Args:
        text (str): transcript

    Returns:
        np.ndarray of shape (T, 768) or (768,)
    """

    if text is None or not text.strip():
        # Return zero embedding if transcript is empty
        return np.zeros(768, dtype=np.float32)

    # SentenceTransformer returns (1, 768) for single input
    embedding = _model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=False
    )

    # Ensure shape consistency
    embedding = np.asarray(embedding, dtype=np.float32)

    return embedding.squeeze()
