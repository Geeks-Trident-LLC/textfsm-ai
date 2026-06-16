# textfsm_ai/delivery/engine/engine.py


from textfsm_ai.delivery.assembly.builder import build_delivery_package
from textfsm_ai.delivery.assembly.validator import validate_delivery_package
from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.generation.core.models import GenerationResult


class DeliveryEngine:
    """Assemble a DeliveryPackage from generation + DSL artifacts."""

    def __init__(self, model: str) -> None:
        self._model = model

    def assemble(
        self,
        *,
        mode: str,
        generation: GenerationResult,
        canonical: CanonicalTemplate,
        machine_dsl: MachineDSL,
        human_dsl: HumanDSL,
        recognizer: RecognizerPatterns,
        duration_ms: int = 0,
    ):
        pkg = build_delivery_package(
            mode=mode,
            model=self._model,
            generation=generation,
            canonical=canonical,
            machine_dsl=machine_dsl,
            human_dsl=human_dsl,
            recognizer=recognizer,
            duration_ms=duration_ms,
        )

        validate_delivery_package(pkg)
        return pkg
