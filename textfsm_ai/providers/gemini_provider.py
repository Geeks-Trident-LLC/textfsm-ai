# textfsm_ai/providers/gemini_provider.py
from __future__ import annotations

from typing import Any, Dict

from google import genai

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, api_key: str | None = None):
        self.client = genai.Client(api_key=api_key)

    def supports(self, model: str) -> bool:
        return model.startswith("gemini/")

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        try:
            model_name = model.replace("gemini/", "")
            resp = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            content = resp.text
            return {"content": content, "raw": resp.to_dict()}
        except Exception as exc:
            raise ProviderError(f"Gemini provider failed: {exc}") from exc

    async def generate_async(self, **kwargs):
        return self.generate(**kwargs)
