# textfsm_ai/providers/registry.py

from __future__ import annotations

from typing import Dict, Type

from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.azure_provider import AzureOpenAIProvider
from textfsm_ai.providers.deepseek_provider import DeepSeekProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.groq_provider import GroqProvider
from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider
from textfsm_ai.providers.xai_provider import XAIProvider


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
registry.register(GroqProvider)
registry.register(XAIProvider)


def get_provider_by_name(provider_name: str) -> Type[Provider]:
    provider_name = provider_name.lower()
    try:
        return registry.get(provider_name)
    except KeyError:
        raise ValueError(f"Unknown provider name: {provider_name}")
