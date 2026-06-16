# textfsm_ai/generation/support/generator.py

from textfsm_ai.generation.core.models import GenerationResult

from ..core.models import StructuredResult
from .cleaner import clean_template
from .validator import validate_template


def generate(structured: StructuredResult) -> GenerationResult:
    """
    Final assembly stage:
    - Validate raw template
    - If invalid → clean
    - Validate again
    - Deliver
    """

    raw_template = structured.template

    # 1. Validate raw template
    if validate_template(raw_template):
        return GenerationResult(
            template=raw_template,
            status="valid_raw",
            structured=structured,
        )

    # 2. Clean template
    cleaned = clean_template(raw_template)

    # 3. Validate cleaned template
    if validate_template(cleaned):
        return GenerationResult(
            template=cleaned,
            status="cleaned",
            structured=structured,
        )

    # 4. Still invalid → deliver failure
    return GenerationResult(
        template=cleaned,
        status="invalid",
        structured=structured,
    )
