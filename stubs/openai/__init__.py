"""Lightweight openai package stub for mypy.

This module intentionally keeps runtime behavior minimal and only exposes the
symbols the codebase imports for static checking. Extend as needed.
"""
from typing import Any, Dict

# Re-export the `types` package (mypy will resolve submodules from `stubs/openai/types`).
from . import types


def omit(obj: Dict[str, Any], *keys: str) -> Dict[str, Any]:
    """Return a shallow copy of `obj` without the specified keys."""
    return {k: v for k, v in obj.items() if k not in keys}


Omit = dict  # alias used in the codebase; keep permissive for stubs


class OpenAI:
    """Placeholder AsyncOpenAI/Sync OpenAI client type for stubs."""

    # approximate commonly referenced client attributes used by the project
    conversations: Any | None
    audio: Any | None
    realtime: Any | None


AsyncOpenAI = OpenAI

__all__ = ["omit", "Omit", "types", "AsyncOpenAI"]
