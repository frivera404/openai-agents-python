from typing import Any


class ContentAgent:
    """Handles content generation using an LLM in production."""

    def __init__(self, tools_registry=None):
        self.tools = tools_registry

    def handle(self, payload: dict[str, Any]) -> dict:
        prompt = payload.get("prompt") or payload.get("message")
        if not prompt:
            return {"status": "error", "reason": "empty prompt"}
        # In prod call OpenAI Responses API or another LLM tool
        return {"status": "success", "content": f"Generated content for: {prompt[:120]}"}
