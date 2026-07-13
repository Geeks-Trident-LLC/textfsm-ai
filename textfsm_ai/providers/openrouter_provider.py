# textfsm_ai/providers/openrouter_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class OpenRouterProvider(OpenAICompatProvider, ModelListingMixin):
    """
    OpenRouter provider using the OpenAI-compatible API surface.

    OpenRouter is a model aggregator/router: it re-exposes models from
    many upstream providers (OpenAI, Anthropic, Google, Meta, Mistral,
    DeepSeek, xAI, Qwen, etc.) under a single "vendor/model" namespace,
    plus its own "openrouter/auto" meta-model that lets OpenRouter pick
    the best underlying model for a given request.

    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "openrouter"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.openrouter.default,
    ):
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if api_key is None:
            raise ValueError("OPENROUTER_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "OpenRouterProvider":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        return cls(api_key, MODEL.openrouter.default)

    # ---------------------------------------------------------
    # Fetch latest models from OpenRouter's OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
