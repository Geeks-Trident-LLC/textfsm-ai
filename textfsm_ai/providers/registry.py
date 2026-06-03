from __future__ import annotations

from typing import Dict, Type

from textfsm_ai.orchestrator.provider import Provider

from .anthropic_provider import AnthropicProvider
from .azure_provider import AzureOpenAIProvider
from .gemini_provider import GeminiProvider
from .openai_compat_provider import OpenAICompatProvider
from .openai_provider import OpenAIProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, Type[Provider]] = {}

    def register(self, provider_cls: Type[Provider]) -> None:
        name = provider_cls.name
        if not name:
            raise ValueError(f"Provider {provider_cls} has empty name")
        self._providers[name] = provider_cls

    def get(self, name: str) -> Type[Provider]:
        try:
            return self._providers[name]
        except KeyError:
            raise KeyError(f"Unknown provider: {name}") from None

    def all(self) -> Dict[str, Type[Provider]]:
        return dict(self._providers)


registry = ProviderRegistry()

registry.register(OpenAIProvider)
registry.register(AnthropicProvider)
registry.register(GeminiProvider)
registry.register(AzureOpenAIProvider)
registry.register(OpenAICompatProvider)
