from __future__ import annotations

from typing import Dict, Type

from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.azure_provider import AzureOpenAIProvider
from textfsm_ai.providers.deepseek_provider import DeepSeekProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, Type[Provider]] = {}

    def register(self, provider_cls: Type[Provider]) -> None:
        self._providers[provider_cls.name] = provider_cls

    def get(self, name: str) -> Type[Provider]:
        return self._providers[name]

    def all(self) -> Dict[str, Type[Provider]]:
        return dict(self._providers)


registry = ProviderRegistry()
registry.register(OpenAIProvider)
registry.register(OpenAICompatProvider)
registry.register(AzureOpenAIProvider)
registry.register(AnthropicProvider)
registry.register(GeminiProvider)
registry.register(DeepSeekProvider)


def get_provider_for_model(model: str) -> Type[Provider]:
    """
    Determine provider based on model prefix.
    """
    model = model.lower()

    if model.startswith("deepseek"):
        return registry.get("deepseek")

    if model.startswith("gpt") or model.startswith("o"):
        return registry.get("openai")

    if model.startswith("claude"):
        return registry.get("anthropic")

    if model.startswith("gemini"):
        return registry.get("gemini")

    raise ValueError(f"Unknown model provider for model: {model}")
