# textfsm_ai/providers/bedrock_provider.py

from __future__ import annotations

import asyncio
import os
from typing import Any, List, Optional

import boto3

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class BedrockProvider(Provider, ModelListingMixin):
    """
    Amazon Bedrock provider using the native `boto3` bedrock-runtime
    Converse API (Shape B).

    Unlike every other provider, Bedrock authenticates via AWS's own
    credential chain (AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/
    AWS_SESSION_TOKEN env vars, ~/.aws/credentials, or an IAM role) rather
    than a project-level API key - boto3 resolves credentials on its own,
    so this provider never handles a secret directly. The only
    Bedrock-specific parameter is `region`, since every Bedrock call is
    region-scoped. This app resolves it from its own app-namespaced
    BEDROCK_REGION/BEDROCK_DEFAULT_REGION env vars (not boto3's own
    AWS_REGION/AWS_DEFAULT_REGION, since region_name is always passed
    explicitly to boto3.client() below, boto3 never gets a chance to fall
    back to its own env vars in this code path).

    boto3 has no native async client, so `generate()` wraps the sync
    `converse()` call in `asyncio.to_thread`, same as AzureOpenAIProvider.
    """

    name = "bedrock"

    def __init__(
        self,
        region: Optional[str] = None,
        default_model: str = MODEL.bedrock.default,
    ) -> None:
        region = (
            region or os.getenv("BEDROCK_REGION") or os.getenv("BEDROCK_DEFAULT_REGION")
        )
        if not region:
            raise ValueError(
                "AWS region is not set (pass region= or set BEDROCK_REGION/"
                "BEDROCK_DEFAULT_REGION)"
            )

        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.region = region
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            return await asyncio.to_thread(self._converse, prompt, model, **kwargs)
        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            return self._converse(prompt, model, **kwargs)
        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def _converse(self, prompt: str, model: str, **kwargs: Any) -> dict:
        max_tokens = kwargs.pop("max_tokens", 2048)
        temperature = kwargs.pop("temperature", 0.2)

        response = self.client.converse(
            modelId=model or self.default_model,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
            **kwargs,
        )

        content_blocks = response["output"]["message"]["content"]
        content = "".join(block.get("text", "") for block in content_blocks)
        usage = response.get("usage", {})

        return {
            "content": content,
            "usage": {
                "prompt_tokens": usage.get("inputTokens"),
                "completion_tokens": usage.get("outputTokens"),
                "total_tokens": usage.get("totalTokens"),
            },
            "raw": response,
        }

    @classmethod
    def from_env(cls) -> "BedrockProvider":
        region = os.getenv("BEDROCK_REGION") or os.getenv("BEDROCK_DEFAULT_REGION")
        if not region:
            raise RuntimeError("BEDROCK_REGION or BEDROCK_DEFAULT_REGION is not set")

        return cls(region, MODEL.bedrock.default)

    # ---------------------------------------------------------
    # Fetch latest models from Bedrock's control-plane
    # list_foundation_models() endpoint (a separate service, "bedrock",
    # from the data-plane "bedrock-runtime" client used for generation).
    # ---------------------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        control_client = boto3.client("bedrock", region_name=self.region)
        summaries = control_client.list_foundation_models().get("modelSummaries", [])
        return [m["modelId"] for m in summaries]
