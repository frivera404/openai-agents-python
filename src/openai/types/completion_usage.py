from __future__ import annotations

from dataclasses import dataclass

from . import BaseModel


@dataclass
class CompletionUsage(BaseModel):
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
