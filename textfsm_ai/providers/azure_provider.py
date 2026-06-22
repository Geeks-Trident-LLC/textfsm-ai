# textfsm_ai/providers/azure_provider.py

from __future__ import annotations

import asyncio
import os
from typing import Any, List

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class AzureOpenAIProvider(Provider, ModelListingMixin):
    name = "azure"

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        api_version: str,
        default_model: str = MODEL.openai.default,
    ) -> None:
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version=api_version,
        )
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.api_version = api_version
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            # Azure SDK is synchronous → run in thread
            result = await asyncio.to_thread(
                self.client.complete,
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = result.choices[0].message.content
            usage = getattr(result, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "input_tokens", None),
                    "completion_tokens": getattr(usage, "output_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                },
                "raw": result,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            result = self.client.complete(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = result.choices[0].message.content
            usage = getattr(result, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "input_tokens", None),
                    "completion_tokens": getattr(usage, "output_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                },
                "raw": result,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    # -----------------------------
    # 3. from_env() for CLI
    # -----------------------------
    @classmethod
    def from_env(cls) -> "AzureOpenAIProvider":
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set")
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not set")

        return cls(api_key=api_key, endpoint=endpoint, api_version=api_version)

    # -----------------------------
    # 4. Deployment-based listing (--latest-raw)
    # -----------------------------
    def fetch_latest_models(self) -> List[str]:
        models = self.client.models.list()
        return [m.id for m in models]
