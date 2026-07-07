# textfsm_ai/dsl/controller/dsl_controller.py

from __future__ import annotations

from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.dsl.engine import dsl_engine as engine
from textfsm_ai.generation.core.models import GenerationPipeline


class DSLController:
    """High-level orchestrator for DSL operations."""

    def run(self, gen: GenerationPipeline) -> DSLPipeline:
        if not gen.ready or gen.last_stage is None:
            return DSLPipeline(reason=f"GENERATION-ERROR: {gen.reason}", ready=False)

        dsl = engine.run(gen.last_stage.template, gen.last_stage.records)

        return DSLPipeline(dsl=dsl, reason=f"{dsl.reason}", ready=dsl.ready)
