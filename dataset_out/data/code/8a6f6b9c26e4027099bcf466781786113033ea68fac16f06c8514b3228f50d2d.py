from __future__ import annotations

from typing import Any


class ChatCompletionMessageParam(dict[str, Any]):
    pass


class ChatCompletionAssistantMessageParam(ChatCompletionMessageParam):
    def __init__(self, *, role: str, content: Any | None = None) -> None:
        super().__init__(role=role)
        if content is not None:
            self["content"] = content


class ChatCompletionUserMessageParam(ChatCompletionMessageParam):
    def __init__(self, *, role: str, content: Any) -> None:
        super().__init__(role=role, content=content)


class ChatCompletionSystemMessageParam(ChatCompletionMessageParam):
    def __init__(self, *, role: str, content: Any) -> None:
        super().__init__(role=role, content=content)


class ChatCompletionDeveloperMessageParam(ChatCompletionMessageParam):
    def __init__(self, *, role: str, content: Any) -> None:
        super().__init__(role=role, content=content)


class ChatCompletionToolMessageParam(ChatCompletionMessageParam):
    def __init__(self, *, role: str, tool_call_id: str, content: Any) -> None:
        super().__init__(role=role, tool_call_id=tool_call_id, content=content)


class ChatCompletionMessageToolCallParam(dict[str, Any]):
    def __init__(self, *, id: str, type: str, function: dict[str, Any]) -> None:
        super().__init__(id=id, type=type, function=function)


class ChatCompletionToolChoiceOptionParam(dict[str, Any]):
    pass
