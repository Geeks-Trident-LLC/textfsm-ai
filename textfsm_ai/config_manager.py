# textfsm_ai/config_manager.py

from pathlib import Path

from textfsm_ai.user_config import UserConfig, load_user_config, save_user_config

CONFIG_DIR = Path.home() / ".textfsm-ai"


def ensure_config_dir() -> Path:
    CONFIG_DIR.mkdir(exist_ok=True)
    return CONFIG_DIR


def save_config(name: str, cfg: UserConfig) -> Path:
    """
    Save a user config (provider, model, api_key) into ~/.textfsm-ai/<name>.config
    """
    ensure_config_dir()
    path = CONFIG_DIR / f"{name}.config"
    save_user_config(path, cfg)
    return path


def list_configs() -> list[Path]:
    """
    List all user config files in ~/.textfsm-ai/
    """
    if not CONFIG_DIR.exists():
        return []
    return sorted(CONFIG_DIR.glob("*.config"))


def load_named_config(name: str) -> UserConfig:
    """
    Load ~/.textfsm-ai/<name>.config
    """
    path = CONFIG_DIR / f"{name}.config"
    return load_user_config(path)
