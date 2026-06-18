# textfsm_ai/generation/support/generator.py

from textfsm_ai.generation.core.models import GenerationResult

from ..core.models import StructuredResponse
from .validator import validate_template


def generate(structured: StructuredResponse) -> GenerationResult:
    if not structured.ready:
        return GenerationResult(
            template="",
            records=[],
            metadata=structured,
            reason=structured.reason,
            ready=False,
        )

    template = structured.template
    validator = validate_template(template)
    return GenerationResult(
        template=template,
        records=structured.records,
        metadata=structured,
        reason=validator.reason,
        ready=validator.ready,
    )
