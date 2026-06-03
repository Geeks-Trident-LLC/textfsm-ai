from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OrchestratorRequest:
    model: str
    prompt: str
    temperature: float = 0.2
    max_tokens: int = 1024


@dataclass
class OrchestratorResponse:
    provider: str
    model: str
    raw: Dict[str, Any]
