# textfsm_ai/providers/openai_provider.py

from __future__ import annotations

import os
import re
from typing import Any, List, Optional

from openai import AsyncOpenAI, OpenAI

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class OpenAIProvider(Provider, ModelListingMixin):
    name = "openai"

    def __init__(
        self, api_key: Optional[str] = None, default_model: str = MODEL.openai.default
    ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY is not set")

        self.client = AsyncOpenAI(api_key=api_key)
        self.sync_client = OpenAI(api_key=api_key)

        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return bool(re.search(r"(gpt|o[0-9]+)-", model))

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.choices[0].message.content
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    # ---------------------------------------------------------
    # SYNC GENERATION
    # ---------------------------------------------------------
    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            response = self.sync_client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.choices[0].message.content
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPEN_API_KEY is not set")

        return cls(api_key, MODEL.openai.default)

    # ---------------------------------------------------------
    # Fetch latest models from OpenAI API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        return [m.id for m in self.sync_client.models.list().data]
