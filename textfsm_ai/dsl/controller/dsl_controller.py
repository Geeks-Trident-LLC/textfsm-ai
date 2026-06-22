"""
DSL Controller

Responsible for orchestrating DSL operations:
- canonicalization
- machine DSL extraction
- human DSL rendering
- pattern recognition

The controller delegates all logic to the DSL engine and handles:
- input validation
- error wrapping
- orchestration
- logging (optional)
"""

# textfsm_ai/dsl/controller/dsl_controller.py

from __future__ import annotations

from textfsm_ai.dsl import engine
from textfsm_ai.dsl.core.models import DSLPipeline, DSLStage
from textfsm_ai.generation.core.models import GenerationPipeline


class DSLController:
    """High-level orchestrator for DSL operations."""

    def _fail(self, stages, name, result):
        stage = DSLStage(name=name, result=result, reason=result.reason, ready=False)
        stages.append(stage)
        return DSLPipeline(
            stages=stages, last_stage=stage, reason=stage.reason, ready=False
        )

    def _ok(self, stages, name, result):
        stage = DSLStage(
            name=name, result=result, reason=result.reason, ready=result.ready
        )
        stages.append(stage)
        return stage

    def run(self, gen: GenerationPipeline, debug: bool = False) -> DSLPipeline:
        stages: list[DSLStage] = []

        # -------------------------
        # Stage 0: validate generation
        # -------------------------
        if not gen.ready:
            return self._fail(stages, "validate-generation", gen.last_stage)

        # -------------------------
        # Stage 1: canonicalize template
        # -------------------------
        stage_name = "canonicalize-template"
        sample = gen.sample
        llm_template = gen.last_stage.template if gen.last_stage else ""
        records = gen.last_stage.records if gen.last_stage else []
        canonical = engine.canonicalize_template(llm_template, records)
        if not canonical.ready:
            return self._fail(stages, stage_name, canonical)
        self._ok(stages, stage_name, canonical)

        # -------------------------
        # Stage 2: machine DSL
        # -------------------------
        stage_name = "extract-machine-dsl"
        machine_dsl = engine.build_machine_dsl(canonical)
        if not machine_dsl.ready:
            return self._fail(stages, stage_name, machine_dsl)
        self._ok(stages, stage_name, machine_dsl)

        # -------------------------
        # Stage 3: human DSL
        # -------------------------
        stage_name = "render-human-dsl"
        human_dsl = engine.render_human_dsl(machine_dsl, sample)
        if not human_dsl.ready:
            return self._fail(stages, stage_name, human_dsl)
        self._ok(stages, stage_name, human_dsl)

        # -------------------------
        # Stage 4: recognizer
        # -------------------------
        stage_name = "recognize-patterns"
        recognizer = engine.recognize_patterns(machine_dsl, sample, debug=debug)
        last_stage = self._ok(stages, stage_name, recognizer)

        return DSLPipeline(
            stages=stages,
            last_stage=last_stage,
            reason=last_stage.reason,
            ready=last_stage.ready,
        )
