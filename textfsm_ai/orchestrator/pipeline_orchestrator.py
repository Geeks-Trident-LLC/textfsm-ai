# textfsm_ai/orchestrator/pipeline_orchestrator.py

from __future__ import annotations

from textfsm_ai.delivery.controller.controller import DeliveryController


class PipelineOrchestrator:
    def __init__(
        self, provider_name: str, api_key: str, model: str, max_retries=1
    ) -> None:
        self._controller = DeliveryController(
            provider_name=provider_name,
            api_key=api_key,
            model=model,
            max_tries=max_retries,
        )

    def run(self, sample: str, mode: str):
        return self._controller.run(sample=sample, mode=mode)
