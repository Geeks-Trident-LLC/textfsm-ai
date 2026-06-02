from __future__ import annotations

from typing import List

from textfsm_ai.orchestrator.provider import Provider
from .registry import registry
from .config import OrchestratorConfig, ProviderConfig


def create_provider_instance(cfg: ProviderConfig) -> Provider:
    provider_cls = registry.get(cfg.type)
    # allow name override if needed
    instance = provider_cls(**cfg.params)
    # if you want instance.name to match config name:
    instance.name = cfg.name  # type: ignore[attr-defined]
    return instance


def create_providers_from_config(config: OrchestratorConfig) -> List[Provider]:
    return [create_provider_instance(pcfg) for pcfg in config.providers]
