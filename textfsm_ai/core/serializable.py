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
        # Tell mypy: self is a dataclass instance
        d = asdict(cast(Any, self))

        # Convert Enums to their name
        for k, v in d.items():
            if isinstance(v, Enum):
                d[k] = v.name

        return d

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
