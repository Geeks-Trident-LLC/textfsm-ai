# textfsm_ai/providers/deepseek_provider.py
import time
from typing import Any

from deepseek import DeepSeek

from . import AIResponse


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        self._client = DeepSeek(api_key=api_key)
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
