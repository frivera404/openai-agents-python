from __future__ import annotations

import sys
import types
from typing import Any

from .. import BaseModel


class Response(BaseModel):
    pass


class ResponseUsage(BaseModel):
    pass


class ResponseOutputText(BaseModel):
    pass


class ResponseOutputRefusal(BaseModel):
    pass


class ResponseOutputMessage(BaseModel):
    pass


class ResponseFunctionToolCall(BaseModel):
    pass


class ResponseFunctionWebSearch(BaseModel):
    pass


class ResponseFileSearchToolCall(BaseModel):
    pass


class ResponseComputerToolCall(BaseModel):
    pass


class ResponseCompletedEvent(BaseModel):
    pass


class ResponseCreatedEvent(BaseModel):
    pass


class ResponseOutputItemAddedEvent(BaseModel):
    pass


class ResponseContentPartAddedEvent(BaseModel):
    pass


class ResponseContentPartDoneEvent(BaseModel):
    pass


class ResponseOutputItemDoneEvent(BaseModel):
    pass


class ResponseTextDeltaEvent(BaseModel):
    pass


class ResponseRefusalDeltaEvent(BaseModel):
    pass


class ResponseFunctionCallArgumentsDeltaEvent(BaseModel):
    pass


class ResponseStreamEvent(BaseModel):
    pass


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
    pass


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
    "response_function_call_arguments_delta_event": [
        "ResponseFunctionCallArgumentsDeltaEvent"
    ],
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
