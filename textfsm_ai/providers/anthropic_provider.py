# textfsm_ai/providers/anthropic_provider.py

from __future__ import annotations

import os
from typing import Any, List, Optional

from anthropic import Anthropic, AsyncAnthropic

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class AnthropicProvider(Provider, ModelListingMixin):
    name = "anthropic"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.anthropic.default,
    ) -> None:
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if api_key is None:
            raise ValueError("ANTHROPIC_API_KEY is not set")

        self.client = AsyncAnthropic(api_key=api_key)
        self.sync_client = Anthropic(api_key=api_key)
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        kwargs.setdefault("temperature", 0.2)
        kwargs.setdefault("max_tokens", 2048)

        try:
            response = await self.client.messages.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            # Anthropic returns a list of content blocks
            content = response.content[0].text

            usage = getattr(response, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "input_tokens", None),
                    "completion_tokens": getattr(usage, "output_tokens", None),
                    "total_tokens": (
                        (usage.input_tokens or 0) + (usage.output_tokens or 0)
                        if usage
                        else None
                    ),
                },
                "raw": response,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        kwargs.setdefault("temperature", 0.2)
        kwargs.setdefault("max_tokens", 2048)

        try:
            response = self.sync_client.messages.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.content[0].text
            usage = getattr(response, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "input_tokens", None),
                    "completion_tokens": getattr(usage, "output_tokens", None),
                    "total_tokens": (
                        (usage.input_tokens or 0) + (usage.output_tokens or 0)
                        if usage
                        else None
                    ),
                },
                "raw": response,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls) -> "AnthropicProvider":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return cls(api_key, MODEL.anthropic.default)

    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
