from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from textfsm_ai.orchestrator.types import OrchestratorResponse


class Provider(ABC):
    """
    Async-first base interface for all AI model providers.
    """

    name: str

    @abstractmethod
    def supports(self, model: str) -> bool:
        """
        Return True if this provider can serve the given model identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> OrchestratorResponse:
        """
        Async text generation call.
        """
        raise NotImplementedError
