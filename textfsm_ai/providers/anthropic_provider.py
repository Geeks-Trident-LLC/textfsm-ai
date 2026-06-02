# textfsm_ai/providers/anthropic_provider.py
from __future__ import annotations

from typing import Any, Dict

import anthropic

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key)

    def supports(self, model: str) -> bool:
        return model.startswith("anthropic/")

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        try:
            model_name = model.replace("anthropic/", "")
            resp = self.client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            content = resp.content[0].text
            return {"content": content, "raw": resp.model_dump()}
        except Exception as exc:
            raise ProviderError(f"Anthropic provider failed: {exc}") from exc

    async def generate_async(self, **kwargs):
        return self.generate(**kwargs)
