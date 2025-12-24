from __future__ import annotations

from typing import Any


class RequestError(Exception):
    pass


class Timeout:
    def __init__(self, timeout: float | None = None, connect: float | None = None) -> None:
        self.timeout = timeout
        self.connect = connect


class URL(str):
    def __new__(cls, value: str) -> URL:
        return str.__new__(cls, value)


class _AsyncResponse:
    async def aclose(self) -> None:  # pragma: no cover
        return None


class AsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    async def aclose(self) -> None:
        return None


class Client:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self.post = _MockRequest()

    def close(self) -> None:  # pragma: no cover
        return None


class _MockRequest:
    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        return None


__all__ = [
    "AsyncClient",
    "Client",
    "RequestError",
    "Timeout",
    "URL",
]
