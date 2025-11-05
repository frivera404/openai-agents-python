from __future__ import annotations

from dataclasses import dataclass

from .. import BaseModel


@dataclass
class Function(BaseModel):
    name: str
    arguments: str


@dataclass
class ChatCompletionMessageToolCall(BaseModel):
    id: str
    type: str
    function: Function
