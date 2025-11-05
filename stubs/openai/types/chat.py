from __future__ import annotations

from typing import Any

# Minimal placeholders for chat-related types referenced by the codebase.

class ChatCompletionMessageParam(dict[str, Any]):
    pass


class ChatCompletionContentPartParam(dict[str, Any]):
    pass


class ChatCompletionMessage:
    # fields referenced by the code (audio, tool calls, etc.)
    audio: Any | None
    annotations: Any | None
    tool_calls: list[Any] | None
    refusal: Any | None


class ChatCompletionUserMessageParam(dict[str, Any]):
    pass

class ChatCompletionToolMessageParam(dict[str, Any]):
    pass

class ChatCompletionContentPartTextParam(dict[str, Any]):
    pass

class ChatCompletionContentPartImageParam(dict[str, Any]):
    pass

# Add other placeholders as needed.

__all__ = [
    "ChatCompletionMessageParam",
    "ChatCompletionContentPartParam",
    "ChatCompletionMessage",
    "ChatCompletionUserMessageParam",
    "ChatCompletionToolMessageParam",
]
