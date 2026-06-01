# textfsm_ai/user_config.py

import json
from pathlib import Path
from typing import Union


class UserConfig:
    def __init__(self, provider=None, model=None, api_key=None):
        self.provider = provider
        self.model = model
        self.api_key = api_key


def load_user_config(path: Union[str, Path]) -> UserConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return UserConfig(
        provider=data.get("provider"),
        model=data.get("model"),
        api_key=data.get("api_key"),
    )


def save_user_config(path: Union[str, Path], cfg: UserConfig) -> None:
    data = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_key": cfg.api_key,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
