from __future__ import annotations

from typing import Any


class ChatCompletionContentPartParam(dict[str, Any]):
    pass


class ChatCompletionContentPartTextParam(ChatCompletionContentPartParam):
    def __init__(self, *, type: str, text: str) -> None:
        super().__init__(type=type, text=text)


class ChatCompletionContentPartImageParam(ChatCompletionContentPartParam):
    def __init__(self, *, type: str, image_url: dict[str, Any]) -> None:
        super().__init__(type=type, image_url=image_url)
