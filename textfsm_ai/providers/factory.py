# textfsm_ai/providers/factory.py

from __future__ import annotations

from typing import List

from textfsm_ai.orchestrator.provider import Provider

from .config import OrchestratorConfig, ProviderConfig
from .registry import registry


def create_provider_instance(cfg: ProviderConfig) -> Provider:
    """
    Create a provider instance from a ProviderConfig using the registry.
    """
    provider_cls = registry.get(cfg.type)
    if provider_cls is None:
        raise ValueError(f"Unknown provider type: {cfg.type}")

    instance = provider_cls(**cfg.params)

    # Optional: ensure provider.name matches config name
    instance.name = cfg.name  # type: ignore[attr-defined]

    return instance


def create_providers_from_config(config: OrchestratorConfig) -> List[Provider]:
    """
    Create all providers defined in the OrchestratorConfig.
    """
    return [create_provider_instance(pcfg) for pcfg in config.providers]
