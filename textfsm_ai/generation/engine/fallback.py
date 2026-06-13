# textfsm_ai/generation/engine/fallback.py

from typing import Optional

from ..support.cleaner import clean_template
from ..support.extractor import LLMRunResult
from ..support.structured_extractor import StructuredResult, parse_from_response


def run(
    one_pass_result: Optional[LLMRunResult], two_pass_result: Optional[LLMRunResult]
) -> StructuredResult:
    """
    Fallback strategy:
    - Prefer Two-Pass next_response
    - Then Two-Pass response
    - Then One-Pass response
    - Clean aggressively, then parse
    """

    candidate_raw = None
    base = None

    if two_pass_result and two_pass_result.next_response:
        candidate_raw = two_pass_result.next_response
        base = two_pass_result

    elif one_pass_result and one_pass_result.response:
        candidate_raw = one_pass_result.response
        base = one_pass_result

    else:
        # Nothing usable; synthesize empty
        candidate_raw = ""
        base = (
            one_pass_result
            or two_pass_result
            or LLMRunResult(
                provider="unknown",
                model="unknown",
                sample="",
                prompt="fallback",
                response="",
            )
        )

    # Clean aggressively
    cleaned_raw = clean_template(candidate_raw)

    # Parse into structured result
    return parse_from_response(cleaned_raw, base)
