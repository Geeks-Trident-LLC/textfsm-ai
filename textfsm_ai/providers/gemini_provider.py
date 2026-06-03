from __future__ import annotations

import asyncio
from typing import Any

import google.genai as genai

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, api_key: str, default_model: str) -> None:
        self.client = genai.Client(api_key=api_key)
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
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model or self.default_model,
                contents=[{"role": "user", "content": prompt}],
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                **kwargs,
            )

            return {"content": response.text}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc
