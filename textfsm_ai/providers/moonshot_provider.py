# textfsm_ai/providers/moonshot_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class MoonshotProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Moonshot AI (Kimi) provider using the OpenAI-compatible API surface.

    Moonshot's API intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ. Uses the global
    api.moonshot.ai endpoint (not the China-only api.moonshot.cn
    endpoint, which bills in RMB).
    """

    name = "moonshot"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.moonshot.default,
    ):
        api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        if api_key is None:
            raise ValueError("MOONSHOT_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "MoonshotProvider":
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise RuntimeError("MOONSHOT_API_KEY is not set")

        return cls(api_key, MODEL.moonshot.default)

    # ---------------------------------------------------------
    # Fetch latest models from Moonshot's OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
