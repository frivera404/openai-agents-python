from typing import Any, Optional

from . import embeddings, vector_db

# Session store remains in-memory for session state
_SESSION_STORE: dict[str, dict] = {}


def write_session(session_id: str, data: dict):
    _SESSION_STORE[session_id] = data


def read_session(session_id: str):
    return _SESSION_STORE.get(session_id)

def _embed_text(text: str) -> list[float]:
    # Delegate to embeddings provider
    return embeddings.get_embedding(text)


def add_long_term(user_id: str, item: dict[str, Any], embedding: Optional[list[float]] = None):
    """Add an item to the long-term (vector) store. Item should NOT contain secrets.

    Args:
        user_id: user identifier
        item: metadata dict describing the memory item
        embedding: optional precomputed vector; if None a fallback embedding will be used
    """
    text = item.get("text") or item.get("message") or str(item)
    vec = embedding or _embed_text(text)
    vid = vector_db.make_vector_id()
    vector_db.upsert(user_id, vid, vec, item)


def query_long_term(
    user_id: str, query: str = "", limit: int = 10, embedding: Optional[list[float]] = None
) -> list[dict[str, Any]]:
    """Query the vector DB for the user's most relevant memory items.

    Returns a list of metadata dictionaries with added `_score` field.
    """
    vec = embedding or _embed_text(query)
    results = vector_db.query(user_id, vec, top_k=limit)
    return [{**meta, "_score": score} for meta, score in results]
