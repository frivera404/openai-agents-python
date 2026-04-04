from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import BaseModel


@dataclass
class CompletionUsage(BaseModel):
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
    # Optional detailed breakdown fields that show up in some code paths.
    prompt_tokens_details: Any | None = None
    completion_tokens_details: Any | None = None
    # Alternate naming sometimes used upstream
    completion_tokens_detail: Any | None = None
