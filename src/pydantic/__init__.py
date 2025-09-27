from __future__ import annotations

import json
from typing import Any, Generic, TypeVar


class ValidationError(Exception):
    pass


class FieldInfo:
    def __init__(
        self,
        *,
        default: Any = ...,
        default_factory: Any = None,
        description: str | None = None,
    ) -> None:
        self.default = default
        self.default_factory = default_factory
        self.description = description


class BaseModel:
    __field_info__: dict[str, FieldInfo] = {}

    def __init__(self, **data: Any) -> None:
        values = dict(data)
        field_info = getattr(self.__class__, "__field_info__", {})
        for name, info in field_info.items():
            if name in values:
                value = values.pop(name)
            elif info.default is not ...:
                value = info.default
            elif info.default_factory is not None:
                value = info.default_factory()
            else:
                raise ValidationError(f"Missing field: {name}")
            setattr(self, name, value)
        for name, value in values.items():
            setattr(self, name, value)

    def model_dump(self, *, exclude_unset: bool = False) -> dict[str, Any]:
        return dict(self.__dict__)

    def model_dump_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent)

    @classmethod
    def model_validate(cls, data: dict[str, Any]) -> "BaseModel":
        return cls(**data)

    @classmethod
    def model_validate_json(cls, json_str: str) -> "BaseModel":
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as exc:  # pragma: no cover - shim
            raise ValidationError(str(exc)) from exc
        if not isinstance(parsed, dict):
            raise ValidationError("Expected JSON object")
        return cls.model_validate(parsed)

    @classmethod
    def model_json_schema(cls) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, info in getattr(cls, "__field_info__", {}).items():
            prop: dict[str, Any] = {}
            if info.description is not None:
                prop["description"] = info.description
            properties[name] = prop
            if info.default is ... and info.default_factory is None:
                required.append(name)
        schema: dict[str, Any] = {"title": cls.__name__, "type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema


def Field(
    default: Any = ...,
    *,
    default_factory: Any | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory, description=description)


def create_model(name: str, **fields: Any) -> type[BaseModel]:
    base = fields.pop("__base__", BaseModel)
    annotations: dict[str, Any] = dict(getattr(base, "__annotations__", {}))
    field_info: dict[str, FieldInfo] = dict(getattr(base, "__field_info__", {}))
    namespace: dict[str, Any] = {"__field_info__": field_info}

    for field_name, value in fields.items():
        if isinstance(value, tuple) and len(value) == 2:
            annotations[field_name] = value[0]
            info = value[1]
        else:
            info = value
        if isinstance(info, FieldInfo):
            field_info[field_name] = info
            if info.default is not ... and info.default_factory is None:
                namespace[field_name] = info.default
        else:
            fi = Field(default=info)
            field_info[field_name] = fi
            namespace[field_name] = fi.default
    namespace["__annotations__"] = annotations
    return type(name, (base,), namespace)


T = TypeVar("T")


class TypeAdapter(Generic[T]):
    def __init__(self, typ: Any) -> None:
        self.typ = typ

    def validate_python(self, value: Any) -> Any:
        return value

    def validate_json(self, json_str: str, experimental_allow_partial: Any | None = None) -> Any:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as exc:  # pragma: no cover - shim
            raise ValidationError(str(exc)) from exc

    def dump_python(self, value: Any) -> Any:
        return value

    def dump_json(self, value: Any, *, indent: int | None = None) -> str:
        return json.dumps(value, indent=indent)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TypeAdapter({self.typ!r})"


__all__ = [
    "BaseModel",
    "Field",
    "TypeAdapter",
    "ValidationError",
    "create_model",
]
