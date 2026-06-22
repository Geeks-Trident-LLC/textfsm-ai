# textfsm_ai/generation/support/generator.py

from textfsm_ai.generation.core.models import GenerationStage

from ..core.models import StructuredResponse
from .validator import validate_template


def generate(structured: StructuredResponse) -> GenerationStage:
    if not structured.ready:
        return GenerationStage(
            template="",
            records=[],
            metadata=structured,
            reason=structured.reason,
            ready=False,
        )

    template = structured.template
    validator = validate_template(template)
    return GenerationStage(
        template=template,
        records=structured.records,
        metadata=structured,
        reason=validator.reason,
        ready=validator.ready,
    )
