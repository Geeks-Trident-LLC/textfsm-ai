# textfsm_ai/providers/groq_provider.py

import os
from typing import List, Optional

from textfsm_ai.models import model as MODEL
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

from .openai_compat_provider import OpenAICompatProvider


class GroqProvider(OpenAICompatProvider, ModelListingMixin):
    """
    Groq provider using the OpenAI-compatible API surface.

    Groq hosts open models (Llama, Gemma, Qwen, Mixtral, DeepSeek-distill)
    behind an OpenAI-compatible chat.completions endpoint:
    - same request format
    - same response format
    - same chat.completions.create()
    - same models.list()
    Only the base_url and API key differ.
    """

    name = "groq"

    def __init__(
        self, api_key: Optional[str] = None, default_model: str = MODEL.groq.default
    ):
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if api_key is None:
            raise ValueError("GROQ_API_KEY is not set")

        super().__init__(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            default_model=default_model,
        )

    @classmethod
    def from_env(cls) -> "GroqProvider":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")

        return cls(api_key, MODEL.groq.default)

    # ---------------------------------------------------------
    # Fetch latest models from Groq's OpenAI-compatible API
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.sync_client.models.list().data
        return [m.id for m in models]
