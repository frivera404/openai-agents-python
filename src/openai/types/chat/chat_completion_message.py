from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .. import BaseModel
from .chat_completion_message_tool_call import ChatCompletionMessageToolCall


@dataclass
class ChatCompletionMessage(BaseModel):
    role: str
    content: Any = None
    refusal: str | None = None
    tool_calls: list[ChatCompletionMessageToolCall] = field(default_factory=list)


ChatCompletionMessageParam = dict[str, Any]
