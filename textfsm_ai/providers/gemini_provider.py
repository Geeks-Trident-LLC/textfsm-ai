# textfsm_ai/providers/gemini_provider.py
import time
from typing import Any

import google.generativeai as genai

from . import AIResponse


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self._model_name = model

    def send(self, prompt: str, **kwargs: Any) -> AIResponse:
        model_name = kwargs.get("model", self._model_name)
        model = genai.GenerativeModel(model_name)
        start = time.perf_counter()

        resp = model.generate_content(prompt)

        latency_ms = int((time.perf_counter() - start) * 1000)
        text = resp.text or ""

        return AIResponse(
            text=text,
            provider=self.name,
            model=model_name,
            latency_ms=latency_ms,
            raw=resp,
        )
