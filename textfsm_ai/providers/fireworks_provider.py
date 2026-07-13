# textfsm_ai/providers/fireworks_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class FireworksProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Fireworks AI provider using the OpenAI-compatible API surface.

    Fireworks' API intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "fireworks"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.fireworks.default,
    ):
        api_key = api_key or os.getenv("FIREWORKS_API_KEY")
        if api_key is None:
            raise ValueError("FIREWORKS_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "FireworksProvider":
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise RuntimeError("FIREWORKS_API_KEY is not set")

        return cls(api_key, MODEL.fireworks.default)

    # ---------------------------------------------------------
    # Fetch latest models from Fireworks' OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
