# textfsm_ai/core/serializable.py

import json
from abc import ABC, abstractmethod


class Serializable(ABC):
    """Base class for objects that can be serialized to dict and JSON."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Subclasses must implement this."""
        raise NotImplementedError

    def to_json(self) -> str:
        """Convert to JSON using the subclass's to_dict()."""
        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
