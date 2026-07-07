# textfsm_ai/delivery/engine/engine.py

from textfsm_ai.delivery.assembly.builder import build_delivery_package
from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.core.package import DeliveryOutput
from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline


class DeliveryEngine:
    """Assemble a DeliveryPackage from generation + DSL artifacts."""

    def assemble(
        self,
        *,
        mode: DeliveryMode,
        model_info,
        generation_pipeline: GenerationPipeline,
        dsl_pipeline: DSLPipeline,
        duration_ms: int = 0,
        as_json: bool = False,
    ) -> DeliveryOutput:
        pkg = build_delivery_package(
            model_info=model_info,
            generation_pipeline=generation_pipeline,
            dsl_pipeline=dsl_pipeline,
            duration_ms=duration_ms,
        )

        if mode is DeliveryMode.QUIET:
            return DeliveryOutput(
                mode=mode,
                output=pkg.quiet.to_json() if as_json else pkg.quiet.to_string(),
                passed=pkg.quiet.status.passed,
                error=pkg.quiet.status.error,
            )

        elif mode is DeliveryMode.DEFAULT:
            return DeliveryOutput(
                mode=mode,
                output=pkg.default.to_json() if as_json else pkg.default.to_string(),
                passed=pkg.default.status.passed,
                error=pkg.default.status.error,
            )

        elif mode is DeliveryMode.INFO:
            return DeliveryOutput(
                mode=mode,
                output=pkg.info.to_json() if as_json else pkg.info.to_string(),
                passed=pkg.info.status.passed,
                error=pkg.info.status.error,
            )

        elif mode is DeliveryMode.DEBUG:
            return DeliveryOutput(
                mode=mode,
                output=pkg.debug.to_json() if as_json else pkg.debug.to_string(),
                passed=pkg.debug.status.passed,
                error=pkg.debug.status.error,
            )

        return DeliveryOutput(
            mode=mode,
            output=pkg.default.to_json() if as_json else pkg.default.to_string(),
            passed=pkg.default.status.passed,
            error=pkg.default.status.error,
        )
