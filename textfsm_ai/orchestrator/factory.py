from __future__ import annotations

from typing import Dict

from textfsm_ai.orchestrator.orchestrator import (
    Orchestrator,
    create_default_routing_table,
)
from textfsm_ai.orchestrator.provider import Provider
from textfsm_ai.providers.config import OrchestratorConfig
from textfsm_ai.providers.registry import registry


def create_orchestrator_from_config(cfg: OrchestratorConfig) -> Orchestrator:
    """
    Build an async-first orchestrator from configuration.
    """
    providers: Dict[str, Provider] = {}

    for name, provider_cfg in cfg.providers.items():
        provider_cls = registry.get(name)
        providers[name] = provider_cls(**provider_cfg)

    routing_table = create_default_routing_table()
    return Orchestrator(routing_table, providers)


def create_orchestrator(providers):
    """
    Legacy helper used only by unit tests.
    Accepts a list of Provider instances and builds an Orchestrator.
    """
    provider_map = {p.name: p for p in providers}
    routing = create_default_routing_table()
    return Orchestrator(providers=provider_map, routing_table=routing)
