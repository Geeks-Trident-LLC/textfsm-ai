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

from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.dsl.engine import (
    build_machine_dsl,
    canonicalize_template,
    recognize_patterns,
    render_human_dsl,
)
from textfsm_ai.generation.core.models import GenerationResult


class DSLController:
    """High-level orchestrator for DSL operations."""

    def canonicalize(self, gen: GenerationResult) -> CanonicalTemplate:
        template = gen.template
        records = gen.metadata.data.get("parsed_result")
        if not template:
            raise ValueError("template must not be empty")
        return canonicalize_template(template, records)

    def to_machine_dsl(self, canonical: CanonicalTemplate) -> MachineDSL:
        if not isinstance(canonical, CanonicalTemplate):
            raise TypeError("canonical must be a CanonicalTemplate instance")
        return build_machine_dsl(canonical)

    def to_human_dsl(self, machine: MachineDSL, sample: str) -> HumanDSL:
        return render_human_dsl(machine, sample)

    def recognize(
        self,
        machine: MachineDSL,
        sample: str,
        debug: bool = False,
    ) -> RecognizerPatterns:
        return recognize_patterns(machine, sample, debug=debug)
