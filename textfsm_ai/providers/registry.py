# textfsm_ai/providers/registry.py

from __future__ import annotations

from importlib import import_module
from typing import Dict, NamedTuple, Optional, Type

from textfsm_ai.orchestrator.provider import Provider


class _LazySpec(NamedTuple):
    """Where to import a provider class from, and which pip extra installs it."""

    module: str
    class_name: str
    extra: str


# name -> (module path, class name, pip extra that installs its SDK)
#
# Each provider module does its own top-level `import <sdk>` (e.g.
# `import boto3`, `from cohere import ...`). Importing that module is
# deferred until a caller actually asks for that provider by name, so
# `import textfsm_ai` and building this registry never requires every
# provider SDK to be installed - only the one(s) actually used.
_LAZY_PROVIDERS: Dict[str, _LazySpec] = {
    "openai": _LazySpec(
        "textfsm_ai.providers.openai_provider", "OpenAIProvider", "openai"
    ),
    "openai_compat": _LazySpec(
        "textfsm_ai.providers.openai_compat_provider",
        "OpenAICompatProvider",
        "openai",
    ),
    "azure": _LazySpec(
        "textfsm_ai.providers.azure_provider", "AzureOpenAIProvider", "azure"
    ),
    "anthropic": _LazySpec(
        "textfsm_ai.providers.anthropic_provider", "AnthropicProvider", "anthropic"
    ),
    "gemini": _LazySpec(
        "textfsm_ai.providers.gemini_provider", "GeminiProvider", "gemini"
    ),
    "deepseek": _LazySpec(
        "textfsm_ai.providers.deepseek_provider", "DeepSeekProvider", "deepseek"
    ),
    "groq": _LazySpec("textfsm_ai.providers.groq_provider", "GroqProvider", "groq"),
    "xai": _LazySpec("textfsm_ai.providers.xai_provider", "XAIProvider", "xai"),
    "together": _LazySpec(
        "textfsm_ai.providers.together_provider", "TogetherProvider", "together"
    ),
    "fireworks": _LazySpec(
        "textfsm_ai.providers.fireworks_provider", "FireworksProvider", "fireworks"
    ),
    "cerebras": _LazySpec(
        "textfsm_ai.providers.cerebras_provider", "CerebrasProvider", "cerebras"
    ),
    "perplexity": _LazySpec(
        "textfsm_ai.providers.perplexity_provider", "PerplexityProvider", "perplexity"
    ),
    "openrouter": _LazySpec(
        "textfsm_ai.providers.openrouter_provider", "OpenRouterProvider", "openrouter"
    ),
    "moonshot": _LazySpec(
        "textfsm_ai.providers.moonshot_provider", "MoonshotProvider", "moonshot"
    ),
    "mistral": _LazySpec(
        "textfsm_ai.providers.mistral_provider", "MistralProvider", "mistral"
    ),
    "bedrock": _LazySpec(
        "textfsm_ai.providers.bedrock_provider", "BedrockProvider", "bedrock"
    ),
    "cohere": _LazySpec(
        "textfsm_ai.providers.cohere_provider", "CohereProvider", "cohere"
    ),
    "vertexai": _LazySpec(
        "textfsm_ai.providers.vertexai_provider", "VertexAIProvider", "vertexai"
    ),
    "oci": _LazySpec("textfsm_ai.providers.oci_provider", "OCIProvider", "oci"),
}


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, Type[Provider]] = {}
        self._lazy: Dict[str, _LazySpec] = dict(_LAZY_PROVIDERS)

    def register(self, provider_cls: Type[Provider]) -> None:
        self._providers[provider_cls.name] = provider_cls

    def get(self, name: str) -> Type[Provider]:
        if name in self._providers:
            return self._providers[name]

        spec = self._lazy.get(name)
        if spec is None:
            raise KeyError(name)

        try:
            module = import_module(spec.module)
        except ImportError as ex:
            raise ImportError(
                f"Provider {name!r} requires additional dependencies that are "
                f"not installed. Install with: pip install textfsm-ai[{spec.extra}]"
            ) from ex

        provider_cls = getattr(module, spec.class_name)
        self._providers[name] = provider_cls
        return provider_cls

    def all(self) -> Dict[str, Optional[Type[Provider]]]:
        combined: Dict[str, Optional[Type[Provider]]] = {
            name: None for name in self._lazy
        }
        combined.update(self._providers)
        return combined


registry = ProviderRegistry()


def get_provider_by_name(provider_name: str) -> Type[Provider]:
    provider_name = provider_name.lower()
    try:
        return registry.get(provider_name)
    except KeyError:
        raise ValueError(f"Unknown provider name: {provider_name}")
