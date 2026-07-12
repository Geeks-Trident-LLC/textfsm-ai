# textfsm_ai/dsl/infer.py

from typing import Iterable

from ...core.category_matcher import match_token_categories
from ...core.patterns import KEYWORD_TO_BASE, PATTERNS_MAPPING


def infer_base_keyword(tokens):
    if isinstance(tokens, str):
        tokens = [tokens]
    toks = [t for t in tokens if t != ""]
    if not toks:
        return None
    # list of lists, not sets
    per_token = [match_token_categories(tok) for tok in toks]

    # intersection while preserving order
    for key in PATTERNS_MAPPING.keys():
        if all(key in categories for categories in per_token):
            return key
    return None


def infer_base_category(tokens: Iterable[str]):
    kw = infer_base_keyword(tokens)
    if kw is None:
        return None
    return KEYWORD_TO_BASE.get(kw)
