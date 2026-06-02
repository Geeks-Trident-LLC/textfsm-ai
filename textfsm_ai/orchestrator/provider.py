# textfsm_ai/orchestrator/provider.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class Provider(ABC):
    """
    Base interface for all model providers.
    """

    name: str

    @abstractmethod
    def supports(self, model: str) -> bool:
        """
        Return True if this provider can serve the given model identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Synchronous text generation call.
        Must return a dict with at least a 'content' key.
        """
        raise NotImplementedError

    async def generate_async(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Async text generation call.
        Default implementation wraps sync generate; override for true async.
        """
        # naive default: run sync in thread if needed later
        return self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


class ProviderProtocol(Protocol):
    name: str

    def supports(self, model: str) -> bool: ...
    def generate(
        self, prompt: str, *, model: str, temperature: float, max_tokens: int
    ) -> Dict[str, Any]: ...
    async def generate_async(
        self, prompt: str, *, model: str, temperature: float, max_tokens: int
    ) -> Dict[str, Any]: ...
