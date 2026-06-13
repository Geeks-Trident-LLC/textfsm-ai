# textfsm_ai/dsl/category_matcher.py

"""
Token → keyword-category matching based on PATTERNS_MAPPING.

This module replaces the old regex_matcher.py and provides the minimal
functionality required by infer.py and DSL reverse parsing.
"""

import re

from .patterns import PATTERNS_MAPPING

# Precompile patterns once, preserving order
_COMPILED = {
    name: re.compile(f"^{pattern}$") for name, pattern in PATTERNS_MAPPING.items()
}


def match_token_categories(token: str):
    """
    Return a list of keyword names whose regex fully matches the token.

    PATTERNS_MAPPING is ordered, so the returned list preserves precedence.
    """
    matches = []
    for keyword, regex in _COMPILED.items():
        if regex.fullmatch(token):
            matches.append(keyword)
    return matches
