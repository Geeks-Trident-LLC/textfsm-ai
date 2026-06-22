# textfsm_ai/orchestrator/provider.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """
    Async-first base interface for all AI model providers.
    """

    name: str

    # Allow arbitrary constructor signatures
    def __init__(self, *args: object, **kwargs: object) -> None: ...

    @abstractmethod
    def supports(self, model: str) -> bool:
        """
        Return True if this provider can serve the given model identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        """
        Async text generation call.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        raise NotImplementedError

    @classmethod
    def from_env(cls):
        raise NotImplementedError
