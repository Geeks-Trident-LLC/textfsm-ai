# textfsm_ai/providers/anthropic_provider.py
import time
from typing import Any

from anthropic import Anthropic

from . import AIResponse


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str = ""):
        self._client = Anthropic(api_key=api_key)
        self._default_model = model

    def send(self, prompt: str, **kwargs: Any) -> AIResponse:
        model = kwargs.get("model", self._default_model)
        start = time.perf_counter()

        resp = self._client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = int((time.perf_counter() - start) * 1000)

        # Claude returns content as a list of blocks
        text = ""
        if resp.content and len(resp.content) > 0:
            block = resp.content[0]
            if hasattr(block, "text"):
                text = block.text or ""

        return AIResponse(
            text=text,
            provider=self.name,
            model=model,
            latency_ms=latency_ms,
            raw=resp,
        )


def list_anthropic_models(api_key: str) -> list[str]:
    client = Anthropic(api_key=api_key)
    models = client.models.list()
    return [m.id for m in models.data]
