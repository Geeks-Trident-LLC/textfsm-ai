from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from anthropic import Anthropic, AsyncAnthropic

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

ANTHROPIC_PATTERN = re.compile(r"^claude-(opus|sonnet|haiku)-[0-9]+-(.*)?$")


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
            # e.g. response.content = [{"type": "text", "text": "..."}]
            content = response.content[0].text

            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        kwargs.setdefault("max_tokens", 2048)
        try:
            response = self.sync_client.messages.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            # Same structure as async version
            content = response.content[0].text

            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls) -> "AnthropicProvider":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return cls(api_key, MODEL.anthropic.default)

    def fetch_latest_models(self) -> List[str]:
        import anthropic

        client = anthropic.Anthropic()
        return [m.id for m in client.models.list().data]

    def classify_models_with_llm(self, raw_models: List[str]) -> Dict[str, List[str]]:
        groups: dict[str, list[str]] = {
            "quality": [],
            "balance": [],
            "fast": [],
            "thinking": [],
            "other": [],
        }

        for m in raw_models:
            match = ANTHROPIC_PATTERN.match(m)
            if not match:
                groups["other"].append(m)
                continue

            tier = match.group(1)
            if tier == "opus":
                groups["quality"].append(m)
                groups["thinking"].append(m)
            elif tier == "sonnet":
                groups["balance"].append(m)
                groups["thinking"].append(m)
            elif tier == "haiku":
                groups["fast"].append(m)
                groups["thinking"].append(m)
            else:
                groups["other"].append(m)

        # Sort for clean CLI output
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        return groups
