# textfsm_ai/providers/openai_compat_provider.py

from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI, OpenAI

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class OpenAICompatProvider(Provider):
    name = "openai_compat"

    def __init__(self, api_key: str, base_url: str, default_model: str) -> None:
        # async client
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        # sync client
        self.sync_client = OpenAI(api_key=api_key, base_url=base_url)

        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.choices[0].message.content
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            response = self.sync_client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.choices[0].message.content
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc
