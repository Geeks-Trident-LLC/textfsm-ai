# textfsm_ai/config_loader.py
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "textfsm_ai" / "config.yaml"


class AppConfig:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def default_provider(self) -> str:
        return self._data.get("default_provider", "openai")

    @property
    def default_model(self) -> str:
        return self._data.get("default_model", "")

    def provider_model(self, provider: str) -> str | None:
        return self._data.get("providers", {}).get(provider, {}).get("model")


@dataclass
class ProviderConfig:
    provider: str
    model: str
    api_key: str


def load_config(path: str | Path) -> ProviderConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("rb") as f:
        data = tomllib.load(f)

    provider = data.get("provider")
    model = data.get("model")
    api_key = data.get("api_key")

    if not provider:
        raise ValueError("Config missing required field: provider")
    if not model:
        raise ValueError("Config missing required field: model")
    if not api_key:
        raise ValueError("Config missing required field: api_key")

    return ProviderConfig(provider=provider, model=model, api_key=api_key)
