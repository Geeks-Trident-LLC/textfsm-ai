# textfsm_ai/models/model_registry.py

from functools import lru_cache
from pathlib import Path

import yaml


class ModelRegistry:
    @staticmethod
    @lru_cache(maxsize=1)
    def load():
        path = Path(__file__).parent / "providers.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @classmethod
    def get(cls, provider: str, *path: str):
        """
        Example:
        get("openai", "thinking", "quality", "chat")
        """
        data = cls.load().get(provider, {})
        for key in path:
            if not isinstance(data, dict):
                return []
            data = data.get(key, {})
        return data if isinstance(data, list) else []

    @classmethod
    def alias(cls, name: str):
        return cls.load().get("aliases", {}).get(name)
