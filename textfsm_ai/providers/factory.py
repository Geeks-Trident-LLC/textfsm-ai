# textfsm_ai/providers/factory.py

from __future__ import annotations

from typing import Dict

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

    # Instantiate provider with params
    instance = provider_cls(**cfg.params)

    # Do NOT override instance.name unless explicitly required
    # instance.name = cfg.name  # remove this line

    return instance


def create_providers_from_config(config: OrchestratorConfig) -> Dict[str, Provider]:
    """
    Create all providers defined in the OrchestratorConfig.
    Returns a mapping: provider_name -> provider_instance
    """
    providers: Dict[str, Provider] = {}

    for name, pcfg in config.providers.items():
        providers[name] = create_provider_instance(pcfg)

    return providers
