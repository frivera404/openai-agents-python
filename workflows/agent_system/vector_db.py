"""Vector DB abstraction with an in-memory fallback.

Supports a minimal API:
- `upsert(user_id, vector_id, vector, metadata)`
- `query(user_id, vector, top_k=10)` -> list of (metadata, score)

In production, set environment variables to use a real vector DB (Pinecone, Chroma,
or similar) and implement the provider branch.
"""

import math
import os
import uuid
from typing import Any

_INMEM_STORE: dict[str, list[tuple[str, list[float], dict[str, Any]]]] = {}

# Pinecone adapter (lazy import)
_PINECONE_INDEX = None
_PINECONE_ACTIVE = False


def init_pinecone(api_key: str, environment: str, index_name: str):
    """Initialize Pinecone index. Requires `pinecone-client` package."""
    global _PINECONE_INDEX, _PINECONE_ACTIVE
    try:
        import pinecone

        pinecone.init(api_key=api_key, environment=environment)
        idx = pinecone.Index(index_name)
        _PINECONE_INDEX = idx
        _PINECONE_ACTIVE = True
    except Exception:
        _PINECONE_ACTIVE = False


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def upsert(user_id: str, vector_id: str, vector: list[float], metadata: dict[str, Any]):
    """Insert or update a vector for a user. Uses Pinecone if initialized, else in-memory."""
    if _PINECONE_ACTIVE and _PINECONE_INDEX is not None:
        try:
            # Pinecone expects a list of vectors: (id, vector, metadata)
            _PINECONE_INDEX.upsert(vectors=[(vector_id, vector, {"user_id": user_id, **metadata})])
            return
        except Exception:
            pass

    if user_id not in _INMEM_STORE:
        _INMEM_STORE[user_id] = []
    for i, (vid, _v, _m) in enumerate(_INMEM_STORE[user_id]):
        if vid == vector_id:
            _INMEM_STORE[user_id][i] = (vector_id, vector, metadata)
            return
    _INMEM_STORE[user_id].append((vector_id, vector, metadata))


def query(user_id: str, vector: list[float], top_k: int = 10) -> list[tuple[dict[str, Any], float]]:
    """Return top_k metadata items and similarity scores. Uses Pinecone if active."""
    if _PINECONE_ACTIVE and _PINECONE_INDEX is not None:
        try:
            res = _PINECONE_INDEX.query(vector=vector, top_k=top_k, include_metadata=True)
            out = []
            for match in getattr(res, "matches", []) or res.get("matches", []):
                meta = (
                    match.get("metadata")
                    if isinstance(match, dict)
                    else getattr(match, "metadata", {})
                )
                score = (
                    match.get("score") if isinstance(match, dict) else getattr(match, "score", 0.0)
                )
                out.append((meta, float(score)))
            return out
        except Exception:
            pass

    if user_id not in _INMEM_STORE:
        return []
    scored = []
    for _vid, v, m in _INMEM_STORE[user_id]:
        score = _cosine(vector, v)
        scored.append((m, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def make_vector_id() -> str:
    return str(uuid.uuid4())


def auto_init_from_env():
    """Auto initialize providers from environment variables if present."""
    api_key = os.getenv("PINECONE_API_KEY")
    env = os.getenv("PINECONE_ENV")
    index = os.getenv("PINECONE_INDEX")
    if api_key and env and index:
        init_pinecone(api_key, env, index)


auto_init_from_env()
