from __future__ import annotations

from typing import Any, Dict

from textfsm_ai.orchestrator.errors import (
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from textfsm_ai.orchestrator.provider import Provider


class MockProvider(Provider):
    """
    Test provider that simulates different behaviors:
    - "ok": returns content
    - "rate_limit": raises ProviderRateLimitError
    - "timeout": raises ProviderTimeoutError
    - "error": raises generic RuntimeError
    """

    def __init__(self, name: str, behavior: str = "ok"):
        self.name = name
        self._behavior = behavior
        self.calls = 0

    def supports(self, model: str) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Async generate method used by the async-first orchestrator.
        """
        self.calls += 1

        if self._behavior == "ok":
            return {"content": f"{self.name}:{prompt}"}
        if self._behavior == "rate_limit":
            raise ProviderRateLimitError("rate limited")
        if self._behavior == "timeout":
            raise ProviderTimeoutError("timeout")
        if self._behavior == "error":
            raise RuntimeError("hard failure")

        raise RuntimeError("unknown behavior")
