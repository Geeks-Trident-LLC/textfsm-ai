# textfsm_ai/generation/controller.py

from . import fallback, generator, one_pass, two_pass
from .structured_extractor import parse_from_response
from .validator import validate_template


class Controller:
    def __init__(self, api_key: str, model: str, max_retries: int = 2):
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
            one = one_pass.run(self.api_key, self.model, sample)
            last_one = one

            raw = one.next_response or one.response
            structured = parse_from_response(raw, one)

            if validate_template(structured.template):
                return generator.generate(structured)

        # -------------------------
        # 2. TWO-PASS
        # -------------------------
        for _ in range(self.max_retries):
            two = two_pass.run(self.api_key, self.model, sample)
            last_two = two

            raw = two.next_response or two.response
            structured = parse_from_response(raw, two)

            if validate_template(structured.template):
                return generator.generate(structured)

        # -------------------------
        # 3. FALLBACK
        # -------------------------
        fb_structured = fallback.run(last_one, last_two)
        return generator.generate(fb_structured)
