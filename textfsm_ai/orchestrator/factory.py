from __future__ import annotations

from textfsm_ai.orchestrator.orchestrator import Orchestrator
from textfsm_ai.orchestrator.routing import create_default_routing_table
from textfsm_ai.providers.config import OrchestratorConfig, ProviderConfig
from textfsm_ai.providers.registry import registry


def create_orchestrator_from_config(cfg: OrchestratorConfig) -> Orchestrator:
    providers = {}

    for entry in cfg.providers.values():  # <-- FIXED
        if not isinstance(entry, ProviderConfig):
            raise ValueError(
                f"Invalid provider entry: expected ProviderConfig, got {type(entry)}"
            )

        provider_cls = registry.get(entry.type)
        if provider_cls is None:
            raise ValueError(f"Unknown provider type: {entry.type}")

        params = entry.params or {}
        instance = provider_cls(**params)
        instance.name = entry.name

        providers[entry.name] = instance

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
