# textfsm_ai/generation/support/generator.py

from textfsm_ai.core.serializable import Serializable

from .cleaner import clean_template
from .structured_extractor import StructuredResult
from .validator import validate_template


class GenerationResult(Serializable):
    def __init__(self, template: str, status: str, structured: StructuredResult):
        self.template = template  # final template (raw or cleaned)
        self.status = status  # "valid_raw", "cleaned", "invalid"
        self.structured = structured  # StructuredResult
        #    includes llm_run_result + data

    def is_success(self) -> bool:
        return self.status in ("valid_raw", "cleaned")

    def is_failure(self) -> bool:
        return self.status == "invalid"

    def to_dict(self):
        return {
            "template": self.template,
            "status": self.status,
            "structured": self.structured,
        }


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
