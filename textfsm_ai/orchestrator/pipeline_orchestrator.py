# textfsm_ai/orchestrator/pipeline_orchestrator.py

from __future__ import annotations

from textfsm_ai.delivery.controller.controller import DeliveryController


class PipelineOrchestrator:
    def __init__(self, api_key: str, model: str) -> None:
        self._controller = DeliveryController(api_key=api_key, model=model)

    def run(self, sample: str, mode: str):
        return self._controller.run(sample=sample, mode=mode)
