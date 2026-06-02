# tests/conftest.py or tests/helpers.py
from __future__ import annotations

from typing import Dict, Any

from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.orchestrator.errors import (
    ProviderRateLimitError,
    ProviderTimeoutError,
)


class MockProvider(Provider):
    def __init__(self, name: str, behavior: str = "ok"):
        self.name = name
        self._behavior = behavior
        self.calls = 0

    def supports(self, model: str) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
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

    async def generate_async(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        # reuse sync behavior
        return self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
