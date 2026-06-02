# textfsm_ai/providers/openai_provider.py
from __future__ import annotations

from typing import Any, Dict

from openai import OpenAI

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def supports(self, model: str) -> bool:
        return model.startswith("openai/")

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        try:
            resp = self.client.chat.completions.create(
                model=model.replace("openai/", ""),
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content
            return {"content": content, "raw": resp.model_dump()}
        except Exception as exc:
            raise ProviderError(f"OpenAI provider failed: {exc}") from exc

    async def generate_async(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        # OpenAI SDK v1 does not have async yet → fallback to sync
        return self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
