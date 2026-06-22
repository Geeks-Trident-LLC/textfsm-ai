# textfsm_ai/dsl/engine/dsl_engine.py


from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.dsl.engine.format.dsl_renderer import (
    render_dsl as _render_dsl,
)
from textfsm_ai.dsl.engine.parse.dsl_extractor import (
    extract_machine_dsl as _extract_machine_dsl,
)
from textfsm_ai.dsl.engine.parse.template_canonicalizer import canonicalize
from textfsm_ai.dsl.engine.recognizer.dsl_recognizer import (
    recognize_dsl_patterns as _recognize_dsl_patterns,
)


def canonicalize_template(llm_template: str, records: list) -> CanonicalTemplate:
    """Normalize a raw TextFSM template and attach metadata/variables."""

    result = canonicalize(llm_template=llm_template, records=records)

    return CanonicalTemplate(
        llm_template=llm_template,
        records=records,
        template=result.return_text or "",
        reason=result.reason,
        ready=result.ready,
    )


def build_machine_dsl(canonical: CanonicalTemplate) -> MachineDSL:
    """Build a machine-readable DSL model from a canonical template."""
    dsl = _extract_machine_dsl(canonical.template)
    return MachineDSL(canonical=canonical, dsl=dsl, reason=dsl.reason, ready=dsl.ready)


def render_human_dsl(machine: MachineDSL, sample: str = "") -> HumanDSL:
    """Render a human-readable DSL representation from DSL/template/sample."""

    # If only canonical is provided, build machine DSL first
    dsl = machine.dsl
    if dsl is None:
        dsl = build_machine_dsl(machine.canonical)

    template = machine.canonical.template
    result = _render_dsl(dsl, template, sample)
    return HumanDSL(
        human_dsl=result.return_text or "",
        template=template or None,
        sample=sample or None,
        reason=result.reason,
        ready=result.ready,
    )


def recognize_patterns(
    machine: MachineDSL,
    sample: str = "",
    debug: bool = False,
) -> RecognizerPatterns:
    """Recognize DSL-related patterns from DSL/template/sample."""

    # If only canonical is provided, build machine DSL first
    dsl = machine.dsl

    if dsl is None:
        dsl = build_machine_dsl(machine.canonical.template).dsl

    try:
        patterns, debug_info = _recognize_dsl_patterns(
            dsl=dsl,
            template=machine.canonical.template,
            sample=sample,
            debug=debug,
        )
    except Exception as ex:
        failure = f"{type(ex).__name__}: {ex}"
        return RecognizerPatterns(
            dsl=machine.dsl,
            template=machine.canonical.template,
            sample=sample or None,
            patterns="",
            debug_info={"recognize_dsl_patterns": failure},
            reason=failure,
            ready=False,
        )

    return RecognizerPatterns(
        dsl=machine.dsl,
        template=machine.canonical.template,
        sample=sample or None,
        patterns=patterns,
        debug_info=debug_info if debug else None,
        ready=True,
    )
