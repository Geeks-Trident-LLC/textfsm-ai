from __future__ import annotations

from typing import Any

from textfsm_ai.orchestrator.orchestrator import (
    Orchestrator,
    create_default_routing_table,
)
from textfsm_ai.providers.config import OrchestratorConfig
from textfsm_ai.providers.registry import registry


def create_orchestrator_from_config(cfg: OrchestratorConfig) -> Orchestrator:
    providers = {}

    for entry in cfg.providers:
        # entry may be a string OR a ProviderConfig
        if isinstance(entry, str):
            # Treat string as provider name
            provider_name = entry
            provider_type = entry
            params: dict[str, Any] = {}
        else:
            # Proper ProviderConfig
            provider_name = entry.name
            provider_type = entry.type
            params = entry.params or {}

        provider_cls = registry.get(provider_type)
        if provider_cls is None:
            raise ValueError(f"Unknown provider type: {provider_type}")

        instance = provider_cls(**params)
        instance.name = provider_name

        providers[provider_name] = instance

    routing = create_default_routing_table()
    return Orchestrator(providers=providers, routing_table=routing)


def create_orchestrator(providers):
    """
    Legacy helper used only by unit tests.
    Accepts a list of Provider instances and builds an Orchestrator.
    """
    provider_map = {p.name: p for p in providers}
    routing = create_default_routing_table()
    return Orchestrator(providers=provider_map, routing_table=routing)
