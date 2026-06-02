# textfsm_ai/orchestrator/types.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


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
    raw: Dict[str, Any]
