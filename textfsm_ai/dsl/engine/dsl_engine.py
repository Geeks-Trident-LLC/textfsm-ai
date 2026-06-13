# textfsm_ai/dsl/engine/dsl_engine.py

from typing import Optional

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
        canonical_template=canonical_template,
        records_sample=records,
    )


def build_machine_dsl(template: CanonicalTemplate) -> MachineDSL:
    """Build a machine-readable DSL model from a canonical template."""
    ast = _extract_machine_dsl(template.canonical_template)
    return MachineDSL(canonical_template=template, ast=ast)


def render_human_dsl(
    dsl: Optional[MachineDSL] = None,
    template: Optional[CanonicalTemplate] = None,
    sample: str = "",
) -> HumanDSL:
    """Render a human-readable DSL representation from DSL/template/sample."""
    text = _render_dsl(dsl=dsl.ast, template=template.canonical_template, sample=sample)
    return HumanDSL(
        dsl_text=text,
        template_preview=template.canonical_template if template else None,
        sample=sample or None,
    )


def recognize_patterns(
    dsl: Optional[MachineDSL] = None,
    template: Optional[CanonicalTemplate] = None,
    sample: str = "",
    debug: bool = False,
) -> RecognizerPatterns:
    """Recognize DSL-related patterns from DSL/template/sample."""
    patterns, debug_info = _recognize_dsl_patterns(
        dsl=dsl.ast,
        template=template.canonical_template,
        sample=sample,
        debug=debug,
    )
    return RecognizerPatterns(
        dsl=dsl,
        template=template,
        sample=sample or None,
        patterns=patterns,
        debug_info=debug_info if debug else None,
    )
