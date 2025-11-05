from __future__ import annotations

from dataclasses import dataclass, field

from .. import BaseModel
from ..completion_usage import CompletionUsage


@dataclass
class ChoiceDeltaToolCallFunction(BaseModel):
    name: str | None = None
    arguments: str | None = None


@dataclass
class ChoiceDeltaToolCall(BaseModel):
    index: int
    id: str | None = None
    type: str | None = None
    function: ChoiceDeltaToolCallFunction | None = None


@dataclass
class ChoiceDelta(BaseModel):
    content: str | None = None
    refusal: str | None = None
    tool_calls: list[ChoiceDeltaToolCall] = field(default_factory=list)


@dataclass
class Choice(BaseModel):
    index: int
    delta: ChoiceDelta | None = None
    finish_reason: str | None = None


@dataclass
class ChatCompletionChunk(BaseModel):
    id: str
    created: int
    model: str
    object: str
    choices: list[Choice]
    usage: CompletionUsage | None = None
