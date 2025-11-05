from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any, Generic, TypeVar

import httpx

__all__ = [
    "APIStatusError",
    "AsyncOpenAI",
    "AsyncStream",
    "DefaultAsyncHttpxClient",
    "NOT_GIVEN",
    "NotGiven",
    "OpenAIError",
]


def omit(obj: dict[str, Any], *keys: str) -> dict[str, Any]:
    """Return a shallow copy of `obj` without the specified keys.

    Small helper kept for compatibility with code that calls `openai.omit`.
    """
    return {k: v for k, v in obj.items() if k not in keys}


# Typing-friendly alias used elsewhere in the codebase.
Omit = dict


class OpenAIError(Exception):
    """Minimal stand-in for the real OpenAI error type."""


class APIStatusError(OpenAIError):
    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(message)
        self.request_id = request_id


class NotGiven:
    def __bool__(self) -> bool:  # pragma: no cover - mirrors real sentinel behaviour
        return False

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()


T = TypeVar("T")


class AsyncStream(Generic[T]):
    """Lightweight wrapper that mimics the OpenAI async stream container."""

    def __init__(self, iterator: AsyncIterator[T]):
        self._iterator = iterator

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterator


class _ResponsesClient:
    def __init__(self, owner: AsyncOpenAI) -> None:
        self._owner = owner

    async def create(self, **kwargs: Any) -> Any:  # pragma: no cover - tests monkeypatch
        raise NotImplementedError("Responses.create is stubbed in tests")

    async def stream(self, **kwargs: Any) -> AsyncStream[Any]:  # pragma: no cover - stub
        raise NotImplementedError


class _ChatCompletions:
    def __init__(self, owner: AsyncOpenAI) -> None:
        self._owner = owner

    async def create(self, **kwargs: Any) -> Any:  # pragma: no cover - tests monkeypatch
        raise NotImplementedError("Chat.completions.create is stubbed in tests")


class _ChatClient:
    def __init__(self, owner: AsyncOpenAI) -> None:
        self.completions = _ChatCompletions(owner)


def DefaultAsyncHttpxClient(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
    """Return a vanilla ``httpx.AsyncClient`` for parity with the real SDK."""

    return httpx.AsyncClient(*args, **kwargs)


class AsyncOpenAI:
    """Tiny shim that mimics enough of the OpenAI client for unit tests."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None and http_client is not None:
            raise OpenAIError("An API key is required when constructing AsyncOpenAI with a client")
        self.api_key = api_key
        self.base_url = httpx.URL(base_url or "https://api.openai.local")
        self.organization = organization
        self.project = project
        self._http_client = http_client
        self.responses = _ResponsesClient(self)
        self.chat = _ChatClient(self)
        # Optional client sub-APIs used by parts of the codebase.
        self.conversations: Any | None = None
        self.audio: Any | None = None
        self.realtime: Any | None = None

    async def close(self) -> None:  # pragma: no cover - helper for parity
        if self._http_client is not None:
            await self._http_client.aclose()
