# textfsm_ai/providers/together_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class TogetherProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Together AI provider using the OpenAI-compatible API surface.

    Together's API intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "together"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.together.default,
    ):
        api_key = api_key or os.getenv("TOGETHER_API_KEY")
        if api_key is None:
            raise ValueError("TOGETHER_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.together.xyz/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "TogetherProvider":
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise RuntimeError("TOGETHER_API_KEY is not set")

        return cls(api_key, MODEL.together.default)

    # ---------------------------------------------------------
    # Fetch latest models from Together's OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
