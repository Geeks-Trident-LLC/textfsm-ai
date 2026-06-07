# textfsm_ai/providers/model_listing_mixin.py

from typing import Dict, List

import yaml

from textfsm_ai import BASE_DIR
from textfsm_ai.models.classifier import classify_models
from textfsm_ai.models.tiers import TierGroups


class ModelListingMixin:
    """
    Shared model listing utilities for all providers.

    Responsibilities:
    - Load curated model groups from a central YAML file.
    - Provide a unified classification entry point that delegates to the
      global classifier.
    """

    CURATED_PATH = BASE_DIR / "models" / "curated-models.yaml"

    # ---------------------------------------------
    # Curated model listing
    # ---------------------------------------------
    @classmethod
    def list_models_curated(cls) -> Dict[str, List[str]]:
        """
        Load curated model groups for this provider from the central YAML file.
        """
        if not cls.CURATED_PATH.exists():
            raise FileNotFoundError(f"Curated model file not found: {cls.CURATED_PATH}")

        with open(cls.CURATED_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        provider_name = getattr(cls, "name")
        provider_models = data.get(provider_name)

        if provider_models is None:
            raise KeyError(f"No curated models found for provider '{provider_name}'")

        return provider_models

    # ---------------------------------------------
    # Providers MUST implement this
    # ---------------------------------------------
    def fetch_latest_models(self) -> List[str]:
        """
        Providers must return a flat list of raw model names from their API.
        """
        raise NotImplementedError

    # ---------------------------------------------
    # Unified classifier entry point
    # ---------------------------------------------
    def classify_models(self) -> TierGroups:
        """
        Classify this provider's models into tier groups using the unified classifier.
        """
        raw = self.fetch_latest_models()
        provider_name = getattr(self, "name")
        return classify_models(provider_name, raw)
