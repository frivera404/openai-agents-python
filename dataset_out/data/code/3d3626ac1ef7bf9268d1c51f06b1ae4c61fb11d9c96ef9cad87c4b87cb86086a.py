"""Embeddings provider abstraction.

Uses OpenAI embeddings when available (new or old client). Falls back to a
deterministic hash-based vector for local testing.
"""

import hashlib
import os
from typing import Optional

try:
    from openai import OpenAI as OpenAIClient
except Exception:
    OpenAIClient = None

try:
    import openai as openai_legacy
except Exception:
    openai_legacy = None


def _hash_embed(text: str, dim: int = 1536) -> list[float]:
    # deterministic fallback: use sha256 and expand to dim with simple scaling
    h = hashlib.sha256(text.encode()).digest()
    base = [b / 255.0 - 0.5 for b in h]
    vec = []
    i = 0
    while len(vec) < dim:
        vec.extend(base)
        i += 1
    return vec[:dim]


def get_embedding(text: str, model: Optional[str] = None) -> list[float]:
    """Return embedding vector for text.

    Tries the new OpenAI client first, then the legacy `openai` package, then
    falls back to a hash-based deterministic vector.
    """
    model = model or os.getenv("EMBEDDING_MODEL") or "text-embedding-3-small"
    # New OpenAI client
    if OpenAIClient is not None:
        try:
            client = (
                OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
                if os.getenv("OPENAI_API_KEY")
                else OpenAIClient()
            )
            resp = client.embeddings.create(model=model, input=text)
            # resp.data[0].embedding or resp.output[0].embedding depending on SDK
            emb = None
            if hasattr(resp, "data"):
                emb = (
                    resp.data[0]["embedding"]
                    if isinstance(resp.data[0], dict)
                    else getattr(resp.data[0], "embedding", None)
                )
            if emb is not None:
                return emb
        except Exception:
            pass

    # Legacy openai package
    if openai_legacy is not None:
        try:
            openai_legacy.api_key = os.getenv("OPENAI_API_KEY")
            resp = openai_legacy.Embedding.create(model=model, input=text)
            emb = resp["data"][0]["embedding"]
            return emb
        except Exception:
            pass

    # Fallback deterministic embedding
    return _hash_embed(text, dim=1536)
