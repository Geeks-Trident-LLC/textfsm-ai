from textfsm_ai.generation.core.models import (
    OnePassResult,
    TwoPassResult,
)
from textfsm_ai.generation.engine import (
    fallback,
    one_pass,
    two_pass,
)
from textfsm_ai.generation.support import generator
from textfsm_ai.generation.support.structured_extractor import parse_from_response
from textfsm_ai.generation.support.validator import validate_template


class GenerationController:
    """Stateless orchestrator for generation pipeline."""

    def __init__(self, api_key: str, model: str, max_retries: int = 1):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries

    def run(self, sample: str):
        last_one = None
        last_two = None

        # -------------------------
        # 1. ONE-PASS
        # -------------------------
        for _ in range(self.max_retries):
            one: OnePassResult = one_pass.run(self.api_key, self.model, sample)
            last_one = one

            raw = one.response
            structured = parse_from_response(raw, one)

            if validate_template(structured.template):
                return generator.generate(structured)

        # -------------------------
        # 2. TWO-PASS
        # -------------------------
        for _ in range(self.max_retries):
            two: TwoPassResult = two_pass.run(self.api_key, self.model, sample)
            last_two = two

            raw = two.response_structured
            structured = parse_from_response(raw, two)

            if validate_template(structured.template):
                return generator.generate(structured)

        # -------------------------
        # 3. FALLBACK
        # -------------------------
        fb_structured = fallback.run(last_one, last_two)
        return generator.generate(fb_structured)
