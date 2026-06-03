from __future__ import annotations

import asyncio
from typing import Any

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class AzureOpenAIProvider(Provider):
    name = "azure"

    def __init__(self, api_key: str, endpoint: str, default_model: str) -> None:
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )
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
            # Azure SDK is synchronous → run in thread
            result = await asyncio.to_thread(
                self.client.complete,
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Extract assistant message
            content = result.choices[0].message["content"]

            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc
