from __future__ import annotations

import asyncio
import os
from typing import Any, List, Optional

import google.genai as genai

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class GeminiProvider(Provider, ModelListingMixin):
    name = "gemini"

    def __init__(
        self, api_key: Optional[str] = None, default_model: str = MODEL.gemini.default
    ) -> None:
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)

        self.default_model = default_model

    # ---------------------------------------------------------
    # Orchestrator-required methods
    # ---------------------------------------------------------
    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            config = {}
            if "temperature" in kwargs:
                config["temperature"] = kwargs.pop("temperature")
            if "max_tokens" in kwargs:
                config["max_output_tokens"] = kwargs.pop("max_tokens")

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model or self.default_model,
                contents=prompt,
                config=config,
            )

            return {"content": response.text}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            config = {}
            if "temperature" in kwargs:
                config["temperature"] = kwargs.pop("temperature")
            if "max_tokens" in kwargs:
                config["max_output_tokens"] = kwargs.pop("max_tokens")

            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=prompt,
                config=config,
            )

            return {"content": response.text}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls) -> "GeminiProvider":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        return cls(api_key, MODEL.gemini.default)

    # ---------------------------------------------------------
    # ModelListingMixin methods
    # ---------------------------------------------------------

    def fetch_latest_models(self) -> List[str]:
        models = self.client.models.list()
        return [m.name for m in models]
