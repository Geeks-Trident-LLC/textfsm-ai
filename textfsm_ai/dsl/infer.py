# textfsm_ai/dsl/infer.py

from typing import Iterable

from .category_matcher import match_token_categories
from .expression import KeywordExpression
from .patterns import KEYWORD_TO_BASE, PATTERNS_MAPPING


def infer_base_keyword(tokens):
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


def infer_keyword_expression_from_tokens(tokens: Iterable[str]):
    toks = [t for t in tokens if t != ""]
    if not toks:
        return None

    base = infer_base_category(toks)
    if base is None:
        return None

    count = len(toks)
    is_group = count >= 2

    return KeywordExpression(
        base=base,
        min_count=count,
        max_count=count,
        optional=False,
        is_group=is_group,
    )
