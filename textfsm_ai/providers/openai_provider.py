# textfsm_ai/providers/openai_provider.py
import time
from typing import Any, Optional

from openai import OpenAI

from . import AIResponse


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self._client = OpenAI(api_key=api_key)
        self._default_model = model

    def send(self, prompt: str, **kwargs: Any) -> AIResponse:
        model = kwargs.get("model", self._default_model)
        start = time.perf_counter()

        resp = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = int((time.perf_counter() - start) * 1000)
        text = resp.choices[0].message.content or ""

        return AIResponse(
            text=text,
            provider=self.name,
            model=model,
            latency_ms=latency_ms,
            raw=resp,
        )


def list_openai_models(api_key: str) -> list[str]:
    client = OpenAI(api_key=api_key)
    models = client.models.list()
    return [m.id for m in models.data]
