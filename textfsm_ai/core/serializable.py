# textfsm_ai/core/serializable.py

import json
from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar, cast

from .dotdict import DotDict

T = TypeVar("T", bound="Serializable")


class Serializable:
    """
    Mixin for dataclasses that support dict/JSON serialization
    and deserialization via from_dict().
    """

    def to_dict(self: T) -> Dict[str, Any]:
        d = asdict(cast(Any, self))

        def normalize(value):
            # Enum → name
            if isinstance(value, Enum):
                return value.name

            # Already a dict or convertible via helper
            try:
                return to_dict(value)
            except TypeError:
                pass  # Not convertible by helper, continue below

            # ChatCompletion (OpenAI v1)
            if hasattr(value, "choices") and hasattr(value, "usage"):
                try:
                    return {
                        "id": getattr(value, "id", None),
                        "object": getattr(value, "object", None),
                        "created": getattr(value, "created", None),
                        "model": getattr(value, "model", None),
                        "choices": [
                            {
                                "index": c.index,
                                "message": getattr(c, "message", None),
                                "finish_reason": getattr(c, "finish_reason", None),
                            }
                            for c in value.choices
                        ],
                        "usage": getattr(value, "usage", None),
                    }
                except Exception:
                    return str(value)

            # List → normalize each element
            if isinstance(value, list):
                return [normalize(v) for v in value]

            # Dict → normalize each value
            if isinstance(value, dict):
                return {k: normalize(v) for k, v in value.items()}

            # Primitive → return as is
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value

            # Fallback
            return str(value)

        return {k: normalize(v) for k, v in d.items()}

    def to_dot_dict(self) -> DotDict:
        return DotDict(self.to_dict())

    def list(self) -> List[str]:
        return list(self.to_dict().keys())

    def to_json(self: T) -> str:
        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        # Tell mypy: cls is a dataclass type
        dataclass_fields = fields(cast(Any, cls))

        init_kwargs = {}

        for f in dataclass_fields:
            name = f.name
            value = data.get(name)

            ftype = cast(Any, f.type)

            # Nested dataclass
            if is_dataclass(ftype) and isinstance(value, dict):
                nested_cls = cast(Type[Any], ftype)
                init_kwargs[name] = nested_cls.from_dict(value)

            # Enum
            elif hasattr(ftype, "__members__") and isinstance(value, str):
                init_kwargs[name] = ftype[value]

            else:
                init_kwargs[name] = value

        return cls(**init_kwargs)


def to_dict(response):
    """Convert various LLM response objects into a Python dict."""

    # Primitive
    if isinstance(response, (str, int, float, bool)) or response is None:
        return response

    # Native dict → normalize recursively
    if isinstance(response, dict):
        return {k: to_dict(v) for k, v in response.items()}

    # Native list → normalize recursively
    if isinstance(response, list):
        return [to_dict(v) for v in response]

    # Pydantic v2
    if callable(getattr(response, "model_dump", None)):
        return response.model_dump()

    # Pydantic v1
    if callable(getattr(response, "dict", None)):
        return response.dict()

    # Generic to_dict() (Gemini, Anthropic, custom classes)
    if callable(getattr(response, "to_dict", None)):
        return response.to_dict()

    raise TypeError(f"Don't know how to convert LLM response {type(response)} to dict")


def is_llm_response(response) -> bool:
    """Return True if the object looks like an LLM response model."""

    # Native dict → not an LLM response model
    if isinstance(response, dict):
        return False

    # Native list → not an LLM response model
    if isinstance(response, list):
        return False

    # Pydantic v2
    if callable(getattr(response, "model_dump", None)):
        return True

    # Pydantic v1
    if callable(getattr(response, "dict", None)):
        return True

    # Generic to_dict() (Gemini, Anthropic, custom classes)
    if callable(getattr(response, "to_dict", None)):
        return True

    return False
