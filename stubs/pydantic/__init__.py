from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar
from typing_extensions import Self

T = TypeVar("T")

# Minimal pydantic surface used by the codebase (stubs for mypy only)
class ConfigDict(dict[str, Any]):
    pass


def model_validator(mode: str = "before") -> Callable[[Callable[..., T]], Callable[..., T]]:
    def _decorator(func: Callable[..., T]) -> Callable[..., T]:
        return func

    return _decorator


def Field(default: Any = ..., description: str | None = None, **kwargs: Any) -> Any:
    """Stub for pydantic.Field"""
    return default


class BaseModel:
    model_config: ConfigDict = ConfigDict()

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_copy(self, *, update: dict[str, Any] | None = None) -> Self:
        new = self.__class__(**{**self.__dict__})
        if update:
            for k, v in update.items():
                setattr(new, k, v)
        return new

    def model_validate(self, data: dict[str, Any]) -> Self:
        if isinstance(data, BaseModel):
            return data  # type: ignore[return-value]
        return self.__class__(**data)  # type: ignore[return-value]


class TypeAdapter(Generic[T]):
    def __init__(self, t: Any) -> None:
        self.type = t

    # JSON schema accessor used in the codebase
    @property
    def json_schema(self) -> dict[str, Any]:
        return {}


# Alias used by the codebase
GetCoreSchemaHandler = Callable[..., Any]

# Omit types used in the codebase
class _Omit:
    pass

Omit = _Omit


__all__ = [
    "ConfigDict",
    "model_validator",
    "Field",
    "BaseModel",
    "TypeAdapter",
    "GetCoreSchemaHandler",
    "Omit",
]
