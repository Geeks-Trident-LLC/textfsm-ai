from textfsm_ai.generation.core.models import OnePassResult, TwoPassResult
from textfsm_ai.generation.support.cleaner import clean_template
from textfsm_ai.generation.support.structured_extractor import (
    StructuredResult,
    parse_from_response,
)


def run(one: OnePassResult, two: TwoPassResult) -> StructuredResult:
    """
    Fallback strategy:
    1. Prefer Two-Pass structured response (response_structured)
    2. Then Two-Pass free response (response_free)
    3. Then One-Pass response
    """

    # -------------------------
    # 1. Choose best raw text
    # -------------------------
    if two.response_structured:
        candidate_raw = two.response_structured
        base = two

    elif two.response_free:
        candidate_raw = two.response_free
        base = two

    elif one.response:
        candidate_raw = one.response
        base = one

    else:
        candidate_raw = ""
        base = one or two

    # -------------------------
    # 2. Clean aggressively
    # -------------------------
    cleaned = clean_template(candidate_raw)

    # -------------------------
    # 3. Parse into StructuredResult
    # -------------------------
    return parse_from_response(cleaned, base)
