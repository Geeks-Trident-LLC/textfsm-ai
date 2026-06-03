from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, api_key: str, default_model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
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
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            content = response.choices[0].message["content"]
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc
