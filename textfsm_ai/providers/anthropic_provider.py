from __future__ import annotations

from typing import Any

from anthropic import AsyncAnthropic

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, api_key: str, default_model: str) -> None:
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> dict:
        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Anthropic returns a list of content blocks
            # e.g. response.content = [{"type": "text", "text": "..."}]
            content = response.content[0].text

            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc
