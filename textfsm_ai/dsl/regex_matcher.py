# textfsm_ai/dsl/regex_matcher.py

import re
from typing import Dict, List

from .patterns import PATTERNS_MAPPING

_COMPILED: Dict[str, re.Pattern] = {
    name: re.compile(f"^{pattern}$") for name, pattern in PATTERNS_MAPPING.items()
}


def match_token_categories(token: str) -> List[str]:
    """Return ordered list of pattern names that match this token."""
    matches: List[str] = []
    for name, regex in _COMPILED.items():
        if regex.fullmatch(token):
            matches.append(name)
    return matches


def intersect_matches(tokens: List[str]) -> List[str]:
    """Return ordered common categories across all tokens."""
    if not tokens:
        return []

    per_token = [match_token_categories(tok) for tok in tokens]

    # ordered intersection
    result = []
    for name in PATTERNS_MAPPING.keys():
        if all(name in cats for cats in per_token):
            result.append(name)

    return result
