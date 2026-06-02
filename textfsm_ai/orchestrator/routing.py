# textfsm_ai/orchestrator/routing.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .provider import Provider
from .types import OrchestratorRequest
from .errors import ProviderNotFoundError


@dataclass
class RoutingRule:
    """
    Simple rule: model prefix -> provider name.
    """
    model_prefix: str
    provider_name: str


class RoutingTable:
    """
    Routing table that maps models to providers via prefix rules.
    """

    def __init__(self, rules: List[RoutingRule]):
        self._rules = rules

    def select_provider(
        self,
        request: OrchestratorRequest,
        providers: Dict[str, Provider],
    ) -> Provider:
        model = request.model

        # 1. explicit prefix rules
        for rule in self._rules:
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

    def select_fallback_provider(
        self,
        request: OrchestratorRequest,
        providers: Dict[str, Provider],
        primary: Provider,
    ) -> Optional[Provider]:
        # naive: first other provider that supports the model
        for provider in providers.values():
            if provider is primary:
                continue
            if provider.supports(request.model):
                return provider
        return None