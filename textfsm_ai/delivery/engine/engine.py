# textfsm_ai/delivery/engine/engine.py


from textfsm_ai.delivery.assembly.builder import build_delivery_package
from textfsm_ai.delivery.assembly.validator import validate_delivery_package
from textfsm_ai.delivery.core.package import DeliveryMode
from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline


class DeliveryEngine:
    """Assemble a DeliveryPackage from generation + DSL artifacts."""

    def __init__(self, model: str) -> None:
        self._model = model

    def assemble(
        self,
        *,
        mode: DeliveryMode,
        generation_pipeline: GenerationPipeline,
        dsl_pipeline: DSLPipeline,
        duration_ms: int = 0,
    ):
        generation = generation_pipeline.last_stage

        total = len(dsl_pipeline.stages)
        canonical = dsl_pipeline.stages[0].result if total > 0 else None
        machine_dsl = dsl_pipeline.stages[1].result if total > 1 else None
        human_dsl = dsl_pipeline.stages[2].result if total > 2 else None
        recognizer = dsl_pipeline.stages[3].result if total > 3 else None
        state = (
            dsl_pipeline.last_stage.name or generation_pipeline.last_stage.name
            if generation_pipeline.last_stage
            else ""
        )
        reason = dsl_pipeline.reason or generation_pipeline.reason
        pkg = build_delivery_package(
            mode=mode,
            model=self._model,
            generation=generation,
            canonical=canonical,
            machine_dsl=machine_dsl,
            human_dsl=human_dsl,
            recognizer=recognizer,
            state=state,
            reason=reason,
            duration_ms=duration_ms,
        )

        validate_delivery_package(pkg)
        return pkg
