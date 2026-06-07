from __future__ import annotations

import asyncio
import os
import re
from typing import Any, Dict, List

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin

OPENAI_PATTERN = re.compile(
    r"^gpt-[0-9]+[a-zA-Z]*(\.\d+)?-?(mini|nano|pro|thinking|instant|flash-lite|flash)?$"
)


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

            # Extract assistant message
            content = result.choices[0].message.content

            return {"content": content}

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
            return {"content": content}

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
        client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        )

        return [d.id for d in client.models.list()]

    # -----------------------------
    # 5. Raw listing (--latest)
    # -----------------------------
    def classify_models_with_llm(self, raw_models: List[str]) -> Dict[str, List[str]]:
        groups: dict[str, list[str]] = {
            "quality": [],
            "balance": [],
            "fast": [],
            "thinking": [],
            "other": [],
        }

        for m in raw_models:
            # Match official OpenAI tiers
            match = OPENAI_PATTERN.match(m)
            if not match:
                groups["other"].append(m)
                continue

            tier = match.group(2)

            if tier == "" or tier is None:
                groups["quality"].append(m)
            elif tier == "mini":
                groups["balance"].append(m)
            elif tier == "nano":
                groups["fast"].append(m)
            elif tier in ["instant", "thinking", "pro"]:
                groups["thinking"].append(m)
            else:
                groups["other"].append(m)

        # Sort each group alphabetically
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        # Sort each group alphabetically
        for key in groups:
            if key in ["quality", "balance", "fast"]:
                groups[key].sort(reverse=True)

        return groups
