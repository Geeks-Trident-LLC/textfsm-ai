# textfsm_ai/providers/vertexai_provider.py

from __future__ import annotations

import asyncio
import os
from typing import Any, List, Optional

import google.genai as genai

from textfsm_ai.models import model as MODEL
from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.model_listing_mixin import ModelListingMixin


class VertexAIProvider(Provider, ModelListingMixin):
    """
    Google Vertex AI provider (Shape B).

    Reuses the SAME `google-genai` SDK as native Gemini - `google.genai
    .Client` supports Vertex AI directly via `vertexai=True, project=...,
    location=...`, so no new dependency is needed. Like Bedrock, Vertex AI
    has no project-level API key: when no api_key/credentials are passed,
    the SDK falls back to Google Cloud's Application Default Credentials
    (a service account key file via GOOGLE_APPLICATION_CREDENTIALS,
    `gcloud auth application-default login`, or workload identity on GCP
    infra) - so this provider never handles a secret directly. `project`/
    `location` are resolved from this app's own app-namespaced
    VERTEXAI_PROJECT/VERTEXAI_REGION env vars (not GCP's own
    GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION, since both are always
    passed explicitly to genai.Client() below).

    Vertex AI serves the SAME Gemini model catalog as the native Gemini
    Developer API under IDENTICAL model IDs (e.g. "gemini-2.5-pro") -
    unlike Bedrock/OpenRouter, there is no distinguishing namespace
    prefix. This means Vertex AI models are deliberately NOT added to the
    orchestrator's routing table (native Gemini's "gemini-" rule already
    claims that prefix, and there is no ordering fix for two providers
    serving identical model ID strings) - Vertex AI must always be
    selected explicitly via --provider vertexai, the same treatment given
    to OpenRouter's unclaimed meta-llama/ and mistralai/ vendor slugs.

    generate()/generate_sync() mirror GeminiProvider's implementation
    exactly (same underlying SDK method, same asyncio.to_thread wrapping
    since generate_content() has no genuinely async variant used here) -
    only client construction differs.
    """

    name = "vertexai"

    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        default_model: str = MODEL.vertexai.default,
    ) -> None:
        project = project or os.getenv("VERTEXAI_PROJECT")
        location = location or os.getenv("VERTEXAI_REGION")

        if not project:
            raise ValueError(
                "GCP project is not set (pass project= or set VERTEXAI_PROJECT)"
            )
        if not location:
            raise ValueError(
                "GCP location is not set (pass location= or set VERTEXAI_REGION)"
            )

        self.client = genai.Client(vertexai=True, project=project, location=location)
        self.project = project
        self.location = location
        self.default_model = default_model

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            thinking_budget = kwargs.pop("thinking_budget", 0)
            config = genai.types.GenerateContentConfig(
                temperature=kwargs.pop("temperature", None),
                max_output_tokens=kwargs.pop("max_tokens", None),
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget
                ),
                **kwargs,
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model or self.default_model,
                contents=prompt,
                config=config,
            )

            usage = getattr(response, "usage_metadata", None)

            return {
                "content": response.text,
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_token_count", None),
                    "completion_tokens": getattr(usage, "candidates_token_count", None),
                    "total_tokens": getattr(usage, "total_token_count", None),
                },
                "raw": response,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    def generate_sync(self, prompt: str, *, model: str, **kwargs: Any) -> dict:
        try:
            thinking_budget = kwargs.pop("thinking_budget", 0)
            config = genai.types.GenerateContentConfig(
                temperature=kwargs.pop("temperature", None),
                max_output_tokens=kwargs.pop("max_tokens", None),
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget
                ),
                **kwargs,
            )

            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=prompt,
                config=config,
            )

            usage = getattr(response, "usage_metadata", None)

            return {
                "content": response.text,
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_token_count", None),
                    "completion_tokens": getattr(usage, "candidates_token_count", None),
                    "total_tokens": getattr(usage, "total_token_count", None),
                },
                "raw": response,
            }

        except Exception as exc:
            raise ProviderError(str(exc)) from exc

    @classmethod
    def from_env(cls) -> "VertexAIProvider":
        project = os.getenv("VERTEXAI_PROJECT")
        location = os.getenv("VERTEXAI_REGION")

        if not project:
            raise RuntimeError("VERTEXAI_PROJECT is not set")
        if not location:
            raise RuntimeError("VERTEXAI_REGION is not set")

        return cls(project, location, MODEL.vertexai.default)

    def fetch_latest_models(self) -> List[str]:
        models = self.client.models.list()
        return [m.name for m in models]
