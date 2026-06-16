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
from textfsm_ai.dsl.engine.parse.template_canonicalizer import (
    TemplateCanonicalizer,
)
from textfsm_ai.dsl.engine.recognizer.dsl_recognizer import (
    recognize_dsl_patterns as _recognize_dsl_patterns,
)


def canonicalize_template(template: str, records: list) -> CanonicalTemplate:
    """Normalize a raw TextFSM template and attach metadata/variables."""
    canonical_template = TemplateCanonicalizer().canonicalize(template, records)
    return CanonicalTemplate(
        raw_template=template,
        template=canonical_template,
        records=records,
    )


def build_machine_dsl(canonical: CanonicalTemplate) -> MachineDSL:
    """Build a machine-readable DSL model from a canonical template."""
    ast = _extract_machine_dsl(canonical.template)
    return MachineDSL(canonical=canonical, ast=ast)


def render_human_dsl(machine: MachineDSL, sample: str = "") -> HumanDSL:
    """Render a human-readable DSL representation from DSL/template/sample."""
    if machine.ast is None and machine.canonical.template is None:
        raise ValueError("Either ast or canonical-template must be provided")

    # If only canonical is provided, build machine DSL first
    ast = machine.ast
    if ast is None:
        ast = build_machine_dsl(machine.canonical)

    template = machine.canonical.template
    text = _render_dsl(ast, template, sample)
    return HumanDSL(
        dsl_text=text,
        template_preview=template or None,
        sample=sample or None,
    )


def recognize_patterns(
    machine: MachineDSL,
    sample: str = "",
    debug: bool = False,
) -> RecognizerPatterns:
    """Recognize DSL-related patterns from DSL/template/sample."""
    if machine.ast is None and machine.canonical.template is None:
        raise ValueError("Either ast or canonical-template must be provided")

    # If only canonical is provided, build machine DSL first
    ast = machine.ast
    if ast is None:
        ast = build_machine_dsl(machine.canonical.template)

    patterns, debug_info = _recognize_dsl_patterns(
        ast=ast,
        template=machine.canonical.template,
        sample=sample,
        debug=debug,
    )
    return RecognizerPatterns(
        dsl=machine,
        template=machine.canonical,
        sample=sample or None,
        patterns=patterns,
        debug_info=debug_info if debug else None,
    )
