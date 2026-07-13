# textfsm_ai/providers/cerebras_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class CerebrasProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Cerebras provider using the OpenAI-compatible API surface.

    Cerebras' API intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "cerebras"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.cerebras.default,
    ):
        api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        if api_key is None:
            raise ValueError("CEREBRAS_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "CerebrasProvider":
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise RuntimeError("CEREBRAS_API_KEY is not set")

        return cls(api_key, MODEL.cerebras.default)

    # ---------------------------------------------------------
    # Fetch latest models from Cerebras' OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
