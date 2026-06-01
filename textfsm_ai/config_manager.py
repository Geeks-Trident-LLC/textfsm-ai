# textfsm_ai/config_manager.py

from pathlib import Path

from textfsm_ai.config_loader import ProviderConfig, load_config

CONFIG_DIR = Path.home() / ".textfsm-ai"


def ensure_config_dir() -> Path:
    CONFIG_DIR.mkdir(exist_ok=True)
    return CONFIG_DIR


def save_config(name: str, cfg: ProviderConfig) -> Path:
    ensure_config_dir()
    path = CONFIG_DIR / f"{name}.config"
    content = (
        f'provider = "{cfg.provider}"\n'
        f'model = "{cfg.model}"\n'
        f'api_key = "{cfg.api_key}"\n'
    )
    path.write_text(content, encoding="utf-8")
    return path


def list_configs() -> list[Path]:
    if not CONFIG_DIR.exists():
        return []
    return sorted(CONFIG_DIR.glob("*.config"))


def load_named_config(name: str) -> ProviderConfig:
    path = CONFIG_DIR / f"{name}.config"
    return load_config(path)
