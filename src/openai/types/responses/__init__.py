from __future__ import annotations

import sys
import types
from typing import Any

from .. import BaseModel


class Response(BaseModel):
    id: str | None
    # `output` is a flexible structure in OpenAI responses; keep permissive typing here.
    output: Any | None
    # `usage` holds token usage details
    usage: Any | None
    def model_copy(self, *, update: dict[str, Any] | None = None) -> Response:
        return super().model_copy(update=update)  # type: ignore[return-value]


class ResponseUsage(BaseModel):
    # Minimal usage fields used by the codebase
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None


class ResponseIncludable(BaseModel):
    """Marker-like stub for types that can be passed to 'include' parameters.

    The real SDK exposes a union/enum here; for static checking a permissive
    BaseModel subclass is sufficient.
    """
    pass


# Reasoning-summary related streaming events (seen in mypy output)
class ResponseReasoningSummaryPartAddedEvent(BaseModel):
    delta: Any | None
    summary: Any | None


class ResponseReasoningSummaryPartDoneEvent(BaseModel):
    summary: Any | None


class ResponseReasoningSummaryTextDeltaEvent(BaseModel):
    delta: Any | None


class ResponseOutputText(BaseModel):
    text: str | None


class ResponseOutputRefusal(BaseModel):
    refusal: Any | None


class ResponseOutputMessage(BaseModel):
    content: Any | None


class ResponseFunctionToolCall(BaseModel):
    name: str | None
    arguments: Any | None
    call_id: str | None


class ResponseFunctionWebSearch(BaseModel):
    pass


class ResponseFileSearchToolCall(BaseModel):
    pass


class ResponseComputerToolCall(BaseModel):
    call_id: str | None
    action: Any | None
    pending_safety_checks: Any | None


class ResponseCompletedEvent(BaseModel):
    response: Response | None


class ResponseCreatedEvent(BaseModel):
    response: Response | None


class ResponseOutputItemAddedEvent(BaseModel):
    item: ResponseOutputItem | None


class ResponseContentPartAddedEvent(BaseModel):
    delta: Any | None


class ResponseContentPartDoneEvent(BaseModel):
    pass


class ResponseOutputItemDoneEvent(BaseModel):
    item: ResponseOutputItem | None


class ResponseTextDeltaEvent(BaseModel):
    delta: Any | None


class ResponseRefusalDeltaEvent(BaseModel):
    delta: Any | None


class ResponseFunctionCallArgumentsDeltaEvent(BaseModel):
    arguments: Any | None


class ResponseStreamEvent(BaseModel):
    type: str | None
    response: Response | None
    delta: Any | None

class ResponseOutputItem(BaseModel):
    pass


class ActionClick(BaseModel):
    pass


class ActionDoubleClick(BaseModel):
    pass


class ActionDrag(BaseModel):
    pass


class ActionDragPath(BaseModel):
    pass


class ActionKeypress(BaseModel):
    pass


class ActionMove(BaseModel):
    pass


class ActionScreenshot(BaseModel):
    pass


class ActionScroll(BaseModel):
    pass


class ActionType(BaseModel):
    pass


class ActionWait(BaseModel):
    pass


class ResponseInputItemParam(dict[str, Any]):
    pass


class ResponseInputContentParam(dict[str, Any]):
    pass


class ResponseInputTextParam(ResponseInputContentParam):
    pass


class ResponseInputImageParam(ResponseInputContentParam):
    pass


class ResponseInputAudioParam(ResponseInputContentParam):
    pass


class ResponseInputFileParam(ResponseInputContentParam):
    pass


class ResponseOutputMessageParam(dict[str, Any]):
    pass


class EasyInputMessageParam(dict[str, Any]):
    pass


class ResponseFunctionToolCallParam(dict[str, Any]):
    pass


class ResponseComputerToolCallParam(dict[str, Any]):
    pass


class ResponseFileSearchToolCallParam(dict[str, Any]):
    pass


class ResponseFunctionWebSearchParam(dict[str, Any]):
    pass


class ResponseReasoningItem(BaseModel):
    content: Any | None
    summary: Any | None
    encrypted_content: Any | None


class ResponseReasoningItemParam(dict[str, Any]):
    pass


class Summary(BaseModel):
    pass


class ToolParam(dict[str, Any]):
    pass


class WebSearchToolParam(dict[str, Any]):
    pass


class Filters(dict[str, Any]):
    pass


class RankingOptions(dict[str, Any]):
    pass


class ResponseTextConfigParam(dict[str, Any]):
    pass


class InputTokensDetails(BaseModel):
    pass


class OutputTokensDetails(BaseModel):
    pass


class FunctionCallOutput(dict[str, Any]):
    pass


class ComputerCallOutput(dict[str, Any]):
    pass


class ItemReference(dict[str, Any]):
    pass


class Message(dict[str, Any]):
    pass


class response_create_params:
    ToolChoice = Any


_SUBMODULE_EXPORTS: dict[str, list[str]] = {
    "response_computer_tool_call": [
        "ResponseComputerToolCall",
        "ActionClick",
        "ActionDoubleClick",
        "ActionDrag",
        "ActionDragPath",
        "ActionKeypress",
        "ActionMove",
        "ActionScreenshot",
        "ActionScroll",
        "ActionType",
        "ActionWait",
    ],
    "response_computer_tool_call_param": ["ResponseComputerToolCallParam"],
    "response_file_search_tool_call": ["ResponseFileSearchToolCall"],
    "response_file_search_tool_call_param": ["ResponseFileSearchToolCallParam"],
    "response_function_tool_call": ["ResponseFunctionToolCall"],
    "response_function_tool_call_param": ["ResponseFunctionToolCallParam"],
    "response_function_web_search": ["ResponseFunctionWebSearch"],
    "response_function_web_search_param": ["ResponseFunctionWebSearchParam"],
    "response_output_message": ["ResponseOutputMessage"],
    "response_output_message_param": ["ResponseOutputMessageParam"],
    "response_output_refusal": ["ResponseOutputRefusal"],
    "response_output_text": ["ResponseOutputText"],
    "response_reasoning_item": ["ResponseReasoningItem", "Summary"],
    "response_reasoning_item_param": ["ResponseReasoningItemParam"],
    "response_input_item_param": ["FunctionCallOutput", "ComputerCallOutput"],
    "response_input_param": [
        "FunctionCallOutput",
        "ComputerCallOutput",
        "ItemReference",
        "Message",
    ],
    "response_usage": ["ResponseUsage", "InputTokensDetails", "OutputTokensDetails"],
    "response_text_delta_event": ["ResponseTextDeltaEvent"],
    "response_refusal_delta_event": ["ResponseRefusalDeltaEvent"],
    "response_output_item_added_event": ["ResponseOutputItemAddedEvent"],
    "response_content_part_added_event": ["ResponseContentPartAddedEvent"],
    "response_content_part_done_event": ["ResponseContentPartDoneEvent"],
    "response_output_item_done_event": ["ResponseOutputItemDoneEvent"],
    "response_completed_event": ["ResponseCompletedEvent"],
    "response_created_event": ["ResponseCreatedEvent"],
    "response_function_call_arguments_delta_event": ["ResponseFunctionCallArgumentsDeltaEvent"],
    "response_output_item": ["ResponseOutputItem"],
    "response_stream_event": ["ResponseStreamEvent"],
    "response_text_config_param": ["ResponseTextConfigParam"],
    "file_search_tool_param": ["ToolParam", "Filters", "RankingOptions"],
    "web_search_tool_param": ["WebSearchToolParam", "UserLocation"],
}


class UserLocation(dict[str, Any]):
    pass


def _register_submodules() -> None:
    base = "openai.types.responses.{}"
    for suffix, names in _SUBMODULE_EXPORTS.items():
        module = types.ModuleType(base.format(suffix))
        for name in names:
            module.__dict__[name] = globals()[name]
        sys.modules[module.__name__] = module


_register_submodules()

__all__ = [
    "Response",
    "ResponseUsage",
    "ResponseOutputText",
    "ResponseOutputRefusal",
    "ResponseOutputMessage",
    "ResponseFunctionToolCall",
    "ResponseFunctionWebSearch",
    "ResponseFileSearchToolCall",
    "ResponseComputerToolCall",
    "ResponseCompletedEvent",
    "ResponseCreatedEvent",
    "ResponseOutputItemAddedEvent",
    "ResponseContentPartAddedEvent",
    "ResponseContentPartDoneEvent",
    "ResponseOutputItemDoneEvent",
    "ResponseTextDeltaEvent",
    "ResponseRefusalDeltaEvent",
    "ResponseFunctionCallArgumentsDeltaEvent",
    "ResponseStreamEvent",
    "ResponseOutputItem",
    "ToolParam",
    "WebSearchToolParam",
    "UserLocation",
    "ResponseTextConfigParam",
    "ResponseInputItemParam",
    "ResponseInputContentParam",
    "ResponseInputTextParam",
    "ResponseInputImageParam",
    "ResponseInputAudioParam",
    "ResponseInputFileParam",
    "EasyInputMessageParam",
    "ResponseOutputMessageParam",
    "ResponseFunctionToolCallParam",
    "ResponseComputerToolCallParam",
    "ResponseFileSearchToolCallParam",
    "ResponseFunctionWebSearchParam",
    "ResponseReasoningItem",
    "ResponseReasoningItemParam",
    "Summary",
    "Filters",
    "RankingOptions",
    "InputTokensDetails",
    "OutputTokensDetails",
    "FunctionCallOutput",
    "ComputerCallOutput",
    "ItemReference",
    "Message",
    "response_create_params",
]






