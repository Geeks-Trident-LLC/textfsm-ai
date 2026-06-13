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

from typing import Optional

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


class DSLController:
    """High-level orchestrator for DSL operations."""

    def canonicalize(self, template: str, records: list) -> CanonicalTemplate:
        if not template:
            raise ValueError("template must not be empty")
        return canonicalize_template(template, records)

    def to_machine_dsl(self, canonical: CanonicalTemplate) -> MachineDSL:
        if not isinstance(canonical, CanonicalTemplate):
            raise TypeError("canonical must be a CanonicalTemplate instance")
        return build_machine_dsl(canonical)

    def to_human_dsl(
        self,
        dsl: Optional[MachineDSL] = None,
        canonical: Optional[CanonicalTemplate] = None,
        sample: str = "",
    ) -> HumanDSL:
        if dsl is None and canonical is None:
            raise ValueError("Either dsl or canonical must be provided")

        # If only canonical is provided, build machine DSL first
        if dsl is None:
            dsl = self.to_machine_dsl(canonical)

        return render_human_dsl(dsl=dsl, template=canonical, sample=sample)

    def recognize(
        self,
        dsl: Optional[MachineDSL] = None,
        canonical: CanonicalTemplate | None = None,
        sample: str = "",
        debug: bool = False,
    ) -> RecognizerPatterns:
        if dsl is None and canonical is None:
            raise ValueError("Either dsl or canonical must be provided")

        # If only canonical is provided, build machine DSL first
        if dsl is None:
            dsl = self.to_machine_dsl(canonical)

        return recognize_patterns(
            dsl=dsl,
            template=canonical,
            sample=sample,
            debug=debug,
        )
