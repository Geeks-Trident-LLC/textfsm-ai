# textfsm_ai/providers/deepseek_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


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
        models = self.sync_client.models.list().data
        return [m.id for m in models]
