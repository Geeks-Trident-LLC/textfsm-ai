# textfsm_ai/config_loader.py
from pathlib import Path
from typing import Any

import yaml

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


def load_config() -> AppConfig:
    raw = yaml.safe_load(CONFIG_PATH.read_text())
    return AppConfig(raw)
