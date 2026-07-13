# textfsm_ai/providers/perplexity_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class PerplexityProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Perplexity provider using the OpenAI-compatible API surface.

    Perplexity's API intentionally mirrors the OpenAI API:
    - same request format
    - same response format
    - same chat.completions.create()
    Only the base_url and API key differ. Perplexity does not expose a
    models.list() endpoint, so fetch_latest_models() returns the known
    "sonar" family statically instead of querying the API.
    """

    name = "perplexity"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL.perplexity.default,
    ):
        api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if api_key is None:
            raise ValueError("PERPLEXITY_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "PerplexityProvider":
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise RuntimeError("PERPLEXITY_API_KEY is not set")

        return cls(api_key, MODEL.perplexity.default)

    # ---------------------------------------------------------
    # Perplexity has no models.list() endpoint; return the known
    # "sonar" family statically instead.
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        return [
            "sonar",
            "sonar-pro",
            "sonar-reasoning",
            "sonar-reasoning-pro",
            "sonar-deep-research",
        ]
