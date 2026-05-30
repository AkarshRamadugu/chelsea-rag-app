import numpy as np
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2: lightweight, fast, runs locally — no API key required.
_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Encode a list of text strings into a 2-D float32 numpy array.

    Args:
        texts: List of strings to embed.

    Returns:
        Array of shape (len(texts), embedding_dim).
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.astype("float32")


def embed_query(query: str) -> np.ndarray:
    """
    Encode a single query string into a 1-D float32 numpy array.

    Args:
        query: The user's question or search string.

    Returns:
        1-D embedding vector.
    """
    return embed_texts([query])[0]
