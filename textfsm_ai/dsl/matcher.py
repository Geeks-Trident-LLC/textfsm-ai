# textfsm_ai/dsl/matcher.py

from typing import Iterable

from .expression import KeywordExpression
from .patterns import KEYWORD_TO_BASE
from .regex_matcher import match_token_categories


def token_matches_base_category(token: str, base) -> bool:
    keywords = match_token_categories(token)
    for kw in keywords:
        if KEYWORD_TO_BASE.get(kw) == base:
            return True
    return False


def expression_matches_tokens(expr: KeywordExpression, tokens: Iterable[str]) -> bool:
    toks = [t for t in tokens if t != ""]
    count = len(toks)

    if count == 0:
        return expr.optional

    if count < expr.min_count:
        return False
    if expr.max_count is not None and count > expr.max_count:
        return False

    return all(token_matches_base_category(t, expr.base) for t in toks)
