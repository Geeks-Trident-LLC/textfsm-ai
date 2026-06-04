from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from openai import AsyncOpenAI

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

OPENAI_PATTERN = re.compile(
    r"^gpt-[0-9]+[a-zA-Z]*(\.\d+)?-?(mini|nano|pro|thinking|instant|flash-lite|flash)?$"
)


class OpenAIProvider(Provider, ModelListingMixin):
    name = "openai"

    def __init__(self, api_key: str, default_model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            content = response.choices[0].message["content"]
            return {"content": content}

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPEN_API_KEY is not set")

        default_model = "gpt-5.4-nano"

        return cls(api_key, default_model)

    # ---------------------------------------------------------
    # Fetch latest models from OpenAI API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        from openai import OpenAI

        client = OpenAI()
        return [m.id for m in client.models.list().data]  # OpenAI uses "id", not "name"

    # ---------------------------------------------------------
    # Deterministic classifier (no LLM)
    # ---------------------------------------------------------
    def classify_models_with_llm(self, raw_models: List[str]) -> Dict[str, List[str]]:
        groups: dict[str, list[str]] = {
            "quality": [],
            "balance": [],
            "fast": [],
            "thinking": [],
            "other": [],
        }

        for m in raw_models:
            # Match official OpenAI tiers
            match = OPENAI_PATTERN.match(m)
            if not match:
                groups["other"].append(m)
                continue

            tier = match.group(2)

            if tier == "" or tier is None:
                groups["quality"].append(m)
            elif tier == "mini":
                groups["balance"].append(m)
            elif tier == "nano":
                groups["fast"].append(m)
            elif tier in ["instant", "thinking", "pro"]:
                groups["thinking"].append(m)
            else:
                groups["other"].append(m)

        # Sort each group alphabetically
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        # Sort each group alphabetically
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        return groups
