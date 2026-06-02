from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import os
import yaml


@dataclass
class ProviderConfig:
    name: str
    type: str  # "openai", "anthropic", "gemini", "azure"
    params: Dict[str, Any]


@dataclass
class OrchestratorConfig:
    providers: List[ProviderConfig]


def load_config_from_file(path: str) -> OrchestratorConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    providers_cfg = []
    for item in data.get("providers", []):
        providers_cfg.append(
            ProviderConfig(
                name=item["name"],
                type=item["type"],
                params=item.get("params", {}),
            )
        )

    return OrchestratorConfig(providers=providers_cfg)


def load_config_from_env() -> OrchestratorConfig:
    """
    Minimal env-based config for quick starts.
    """
    providers_cfg: List[ProviderConfig] = []

    if os.getenv("OPENAI_API_KEY"):
        providers_cfg.append(
            ProviderConfig(
                name="openai",
                type="openai",
                params={"api_key": os.getenv("OPENAI_API_KEY")},
            )
        )

    if os.getenv("ANTHROPIC_API_KEY"):
        providers_cfg.append(
            ProviderConfig(
                name="anthropic",
                type="anthropic",
                params={"api_key": os.getenv("ANTHROPIC_API_KEY")},
            )
        )

    if os.getenv("GEMINI_API_KEY"):
        providers_cfg.append(
            ProviderConfig(
                name="gemini",
                type="gemini",
                params={"api_key": os.getenv("GEMINI_API_KEY")},
            )
        )

    if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
        providers_cfg.append(
            ProviderConfig(
                name="azure",
                type="azure",
                params={
                    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                },
            )
        )

    return OrchestratorConfig(providers=providers_cfg)
