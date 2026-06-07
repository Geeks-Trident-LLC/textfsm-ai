# textfsm_ai/providers/deepseek_provider.py

import os
import re
from typing import Dict, List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider

DEEPSEEK_PATTERN = re.compile(r"^deepseek-v[0-9]+-?(pro|flash)?$")


class DeepSeekProvider(OpenAICompatProvider, ModelListingMixin):
    """
    DeepSeek provider using the OpenAI-compatible API surface.

    DeepSeek intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "deepseek"

    def __init__(
        self, api_key: Optional[str] = None, default_model: str = MODEL.deepseek.default
    ):
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if api_key is None:
            raise ValueError("DEEPSEEK_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "DeepSeekProvider":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")

        return cls(api_key, MODEL.deepseek.default)

    # ---------------------------------------------------------
    # Fetch latest models from OpenAI API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
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
            match = DEEPSEEK_PATTERN.match(m)
            if not match:
                groups["other"].append(m)
                continue

            tier = match.group(1)

            if tier == "pro":
                groups["quality"].append(m)
                groups["thinking"].append(m)
            elif tier == "flash":
                groups["balance"].append(m)
                groups["fast"].append(m)
                groups["thinking"].append(m)
            else:
                groups["other"].append(m)

        # Sort each group alphabetically
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        return groups
