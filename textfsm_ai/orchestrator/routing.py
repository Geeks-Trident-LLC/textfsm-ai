# textfsm_ai/orchestrator/routing.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .errors import ProviderNotFoundError
from .provider import Provider
from .types import OrchestratorRequest


@dataclass
class RoutingRule:
    """
    Simple rule: model prefix -> provider name.
    """

    model_prefix: str
    provider_name: str


class RoutingTable:
    def __init__(self, rules):
        self.rules = rules

    def route(self, model: str) -> str:
        for rule in self.rules:
            if model.startswith(rule.model_prefix):
                return rule.provider_name
        raise ValueError(f"No routing rule for model: {model}")

    def select_provider(
        self,
        request: OrchestratorRequest,
        providers: Mapping[str, Provider],
    ) -> Provider:
        model = request.model

        # 1. explicit prefix rules
        for rule in self.rules:
            if model.startswith(rule.model_prefix):
                provider = providers.get(rule.provider_name)
                if provider is None:
                    raise ProviderNotFoundError(
                        f"Routing rule points to unknown provider: {rule.provider_name}"
                    )
                return provider

        # 2. fallback: ask providers if they support the model
        for provider in providers.values():
            if provider.supports(model):
                return provider

        raise ProviderNotFoundError(f"No provider found for model: {model}")


# ---------------------------------------------------------------------------
# Default routing table used by the orchestrator factory
# ---------------------------------------------------------------------------


def create_default_routing_table() -> RoutingTable:
    # Groq hosts open models (Llama, Gemma, Qwen, Mixtral) rather than a
    # single vendor-prefixed family, so it needs one rule per family it
    # serves. None of these collide with another provider's models today;
    # if a future provider hosts the same open-weight models under the
    # same names, these rules will need to be reconciled at that point.
    return RoutingTable(
        rules=[
            RoutingRule("gpt-", "openai"),
            RoutingRule("o1-", "openai"),  # Omni 1
            RoutingRule("o3-", "openai"),  # Omni 3
            RoutingRule("claude-", "anthropic"),
            RoutingRule("gemini-", "gemini"),
            RoutingRule("azure-", "azure"),
            RoutingRule("deepseek-", "deepseek"),
            RoutingRule("llama-", "groq"),
            RoutingRule("gemma", "groq"),
            RoutingRule("qwen-", "groq"),
            RoutingRule("mixtral-", "groq"),
        ]
    )
