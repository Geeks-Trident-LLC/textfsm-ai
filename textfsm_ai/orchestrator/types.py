# textfsm_ai/orchestrator/types.py

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


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

    @property
    def content(self) -> Optional[Any]:
        return self.raw.get("content")

    def to_json(self) -> str:
        return json.dumps(self.raw)
