from __future__ import annotations

from __future__ import annotations

from typing import Any


def _to_dict(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return {k: _to_dict(v) for k, v in value.__dict__.items()}
    if isinstance(value, list):
        return [_to_dict(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_dict(v) for k, v in value.items()}
    return value


class BaseModel:
    """Very small stand-in for the pydantic BaseModel used by the real SDK."""

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def model_dump(self, *, exclude_unset: bool = False) -> dict[str, Any]:
        return _to_dict(self.__dict__)


ChatModel = str


__all__ = ["BaseModel", "ChatModel"]
