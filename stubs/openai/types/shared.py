from __future__ import annotations

from typing import Any, Literal

# Placeholder classes for the openai.types.shared namespace.

class Reasoning:
    effort: Literal["minimal", "low", "medium", "high"] | None
    generate_summary: Literal["auto", "concise", "detailed"] | None
    summary: Literal["auto", "concise", "detailed"] | None


__all__ = ["Reasoning"]