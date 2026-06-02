# textfsm_ai/providers/__init__.py
import json
from dataclasses import asdict, dataclass
from typing import Any, Optional, Protocol


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    latency_ms: Optional[int] = None
    raw: Optional[object] = None

    def to_json(self) -> str:
        """Return a JSON string representation of the response."""
        # Convert dataclass to dict
        data = asdict(self)

        # Raw provider objects are not JSON serializable
        # so convert them to string safely
        if self.raw is not None:
            data["raw"] = str(self.raw)

        return json.dumps(data, ensure_ascii=False, indent=2)

    def __str__(self):
        return self.text


class Provider(Protocol):
    name: str

    def send(self, prompt: str, **kwargs: Any) -> AIResponse: ...
