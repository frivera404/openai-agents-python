"""Minimal runtime shim for `openai._types` imports used in the repo.

This provides lightweight aliases for Body and Query so the package can import
them at runtime during tests and local scripts. These are intentionally permissive
and only used where static typing would normally be sufficient.
"""
from typing import Any

Body = Any
"""Placeholder type alias for request body types."""

Query = Any
"""Placeholder type alias for query parameter types."""

__all__ = ["Body", "Query"]
