from __future__ import annotations

from dataclasses import dataclass

from .. import BaseModel
from ..completion_usage import CompletionUsage
from .chat_completion_message import ChatCompletionMessage


@dataclass
class Choice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: str | None = None


@dataclass
class ChatCompletion(BaseModel):
    id: str
    created: int
    model: str
    object: str
    choices: list[Choice]
    usage: CompletionUsage | None = None
