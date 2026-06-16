# textfsm_ai/orchestrator/pipeline_orchestrator.py

from __future__ import annotations

from textfsm_ai.delivery.engine.engine import DeliveryEngine
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController


class PipelineOrchestrator:
    """
    Top-level orchestrator:
    - Runs generation
    - Runs DSL transformations
    - Runs recognizer
    - Builds final delivery package via DeliveryEngine
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._gen = GenerationController(api_key=api_key, model=model)
        self._dsl = DSLController()
        self._engine = DeliveryEngine(model=model)

    def run(self, sample: str, mode: str):
        # 1. Generation
        gen = self._gen.run(sample)

        # 2. DSL pipeline
        # For now, we derive records (if any) from structured.data; later we can
        # promote this to a first-class field on GenerationResult.
        records = (
            gen.structured.data.get("parsed_result", [])
            if gen.structured and gen.structured.data
            else []
        )

        canonical = self._dsl.canonicalize(gen.template, records)
        machine_dsl = self._dsl.to_machine_dsl(canonical)
        human_dsl = self._dsl.to_human_dsl(
            dsl=machine_dsl,
            canonical=canonical,
            sample=gen.structured.llm_run_result.sample,
        )
        recognizer = self._dsl.recognize(
            dsl=machine_dsl,
            canonical=canonical,
            sample=gen.structured.llm_run_result.sample,
        )

        # 3. Delivery engine
        return self._engine.assemble(
            mode=mode,
            generation=gen,
            canonical=canonical,
            machine_dsl=machine_dsl,
            human_dsl=human_dsl,
            recognizer=recognizer,
        )
