# textfsm_ai/providers/azure_provider.py

from __future__ import annotations

import asyncio
import os
from typing import Any, List

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


def build_azure_endpoint(endpoint: str, deployment: str) -> str:
    """
    Normalize Azure endpoint for azure.ai.inference ChatCompletionsClient.

    If the user passes a full deployment endpoint, return it unchanged.
    If the user passes a base endpoint, append the deployment path.
    """
    endpoint = endpoint.rstrip("/")

    # Case 1: Already a full deployment endpoint
    # Example: https://.../openai/deployments/gpt-4.1-textfsm-ai
    if "/openai/deployments/" in endpoint:
        return endpoint

    # Case 2: Base endpoint → build full deployment endpoint
    return f"{endpoint}/openai/deployments/{deployment}"


class AzureOpenAIProvider(Provider, ModelListingMixin):
    name = "azure"

    def __init__(
        self, api_key: str, endpoint: str, api_version: str, deployment: str
    ) -> None:
        full_endpoint = build_azure_endpoint(endpoint, deployment)
        self.client = ChatCompletionsClient(
            endpoint=full_endpoint,
            credential=AzureKeyCredential(api_key),
            api_version=api_version,
        )
        self.api_key = api_key
        self.endpoint = full_endpoint
        self.api_version = api_version
        self.deployment = deployment

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str = "", **kwargs: Any) -> dict:
        try:
            # Azure SDK is synchronous → run in thread
            result = await asyncio.to_thread(
                self.client.complete,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = result.choices[0].message.content
            usage = getattr(result, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                },
                "raw": result,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str = "", **kwargs: Any) -> dict:
        try:
            result = self.client.complete(
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            content = result.choices[0].message.content
            usage = getattr(result, "usage", None)

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
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

        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        if not deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is not set")

        return cls(
            api_key=api_key,
            endpoint=endpoint,
            api_version=api_version,
            deployment=deployment,
        )

    # -----------------------------
    # 4. Deployment-based listing (--latest-raw)
    # -----------------------------
    def fetch_latest_models(self) -> List[str]:
        return [self.deployment]
