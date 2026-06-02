# textfsm_ai/providers/gemini_provider.py
import time
from typing import Any, Optional

from google import genai

from . import AIResponse


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self._client = genai.Client(api_key=api_key)
        self._default_model = model

    def send(self, prompt: str, **kwargs: Any) -> AIResponse:
        model = kwargs.get("model", self._default_model)
        start = time.perf_counter()

        resp = self._client.models.generate_content(
            model=model,
            contents=prompt,
        )

        latency_ms = int((time.perf_counter() - start) * 1000)
        text = resp.text or ""

        return AIResponse(
            text=text,
            provider=self.name,
            model=model,
            latency_ms=latency_ms,
            raw=resp,
        )


def list_gemini_models(api_key: str) -> list[str]:
    client = genai.Client(api_key=api_key)
    return [m.name for m in client.models.list()]
