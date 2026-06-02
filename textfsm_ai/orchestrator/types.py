from dataclasses import dataclass


@dataclass
class OrchestratorRequest:
    model: str
    prompt: str
    temperature: float = 0.0
    max_tokens: int = 2048


@dataclass
class OrchestratorResponse:
    provider: str
    model: str
    content: str
    raw: dict
