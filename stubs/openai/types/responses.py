from __future__ import annotations

from typing import Any, Dict, Optional

# Placeholder classes for the openai.types.responses namespace.
# Extend with attributes as needed to satisfy mypy attr-defined checks.

class Response:
    id: str | None
    output: Any
    usage: Any


class ResponseStreamEvent:
    type: str
    response: Response | None


class ResponseCompletedEvent(ResponseStreamEvent):
    pass


class ResponseOutputItem:
    pass


class ResponseOutputMessage:
    content: Any


class ResponseOutputText(ResponseOutputMessage):
    text: str


class ResponseOutputRefusal(ResponseOutputMessage):
    refusal: str


class ResponseFunctionToolCall(ResponseOutputItem):
    name: str
    arguments: Any
    call_id: str


class ResponseComputerToolCall(ResponseOutputItem):
    call_id: str
    action: Any
    pending_safety_checks: Any


class ResponseReasoningItem(ResponseOutputItem):
    content: Any
    summary: Optional[str]
    encrypted_content: Optional[Any]


class CompletionUsage:
    prompt_tokens: int | None
    completion_tokens: int | None
    # Older/alternate names sometimes used in code
    prompt_tokens_details: Any | None
    completion_tokens_details: Any | None


# response_create_params placeholder (for ToolChoice etc.)
class response_create_params:
    ToolChoice = Any


# Generic type aliases used in the codebase
ResponseInputItemParam = Dict[str, Any]
ResponseInputTextParam = Dict[str, Any]
ResponseInputImageParam = Dict[str, Any]

__all__ = [
    "Response",
    "ResponseStreamEvent",
    "ResponseCompletedEvent",
    "ResponseOutputItem",
    "ResponseOutputMessage",
    "ResponseOutputText",
    "ResponseOutputRefusal",
    "ResponseFunctionToolCall",
    "ResponseComputerToolCall",
    "ResponseReasoningItem",
    "CompletionUsage",
    "response_create_params",
]
