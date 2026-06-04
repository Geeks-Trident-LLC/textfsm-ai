# textfsm_ai/providers/base.py
from pathlib import Path
from typing import Dict, List

import yaml


class ModelListingMixin:
    """
    Provides curated model listing for all providers using a single YAML file.
    """

    CURATED_PATH = Path(__file__).resolve().parent / "curated-models.yaml"

    @classmethod
    def list_models_curated(cls) -> Dict[str, List[str]]:
        """
        Load curated model groups for this provider from a central YAML file.

        Returns:
            Dict[str, List[str]]: Curated model groups for the provider.
        """
        if not cls.CURATED_PATH.exists():
            raise FileNotFoundError(f"Curated model file not found: {cls.CURATED_PATH}")

        with open(cls.CURATED_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        provider_name = getattr(cls, "name")
        provider_models = data.get(provider_name)
        if not provider_models:
            raise KeyError(f"No curated models found for provider '{provider_name}'")

        return provider_models

    def fetch_latest_models(self) -> List[str]:
        raise NotImplementedError

    def classify_models_with_llm(self, raw_models: List[str]) -> Dict[str, List[str]]:
        raise NotImplementedError
