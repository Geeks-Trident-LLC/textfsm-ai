# textfsm_ai/providers/__init__.py
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    latency_ms: int | None = None
    raw: Any | None = None


class Provider(Protocol):
    name: str

    def send(self, prompt: str, **kwargs: Any) -> AIResponse: ...
