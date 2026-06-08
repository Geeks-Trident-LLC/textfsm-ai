# textfsm_ai/dsl/parser.py

from .aliases import ALIASES
from .expression import KeywordExpression
from .quantity import parse_quantity
from .suffix import parse_suffix

PLURAL_KEYWORDS = {
    "dots",
    "spaces",
    "whitespaces",
    "wss",
    "puncts",
    "digits",
    "letters",
    "alnums",
    "words",
    "mixed-words",
    "non-whitespaces",
    "non-wss",
}


def parse_keyword_expression(expr: str) -> KeywordExpression:
    raw = expr.strip()
    parts = raw.split("-")

    # optional prefix
    optional = False
    if parts and parts[0] == "optional":
        optional = True
        parts = parts[1:]

    if not parts:
        raise ValueError(f"Invalid keyword-expression: {expr!r}")

    # quantity prefix: try range (X-to-Y) then exact (N)
    min_q = max_q = None
    idx = 0

    if len(parts) >= 3:
        candidate = "-".join(parts[0:3])  # e.g. "2-to-4"
        qmin, qmax = parse_quantity(candidate)
        if qmin is not None:
            min_q, max_q = qmin, qmax
            idx = 3

    if min_q is None:
        qmin, qmax = parse_quantity(parts[0])
        if qmin is not None:
            min_q, max_q = qmin, qmax
            idx = 1

    parts = parts[idx:]

    if not parts:
        raise ValueError(f"Invalid keyword-expression: {expr!r}")

    # suffix: -item / -group
    base_keyword_raw = "-".join(parts)
    base_keyword, is_group = parse_suffix(base_keyword_raw)

    if base_keyword not in ALIASES:
        raise ValueError(f"Unknown base keyword: {base_keyword}")

    base = ALIASES[base_keyword]

    # default quantity
    if min_q is None and max_q is None:
        if base_keyword in PLURAL_KEYWORDS:
            min_q, max_q = 1, None
        else:
            min_q, max_q = 1, 1

    # group semantics: if no explicit quantity, group = ≥2
    if is_group and min_q == 1 and max_q == 1:
        min_q, max_q = 2, None

    return KeywordExpression(
        base=base,
        min_count=min_q or 1,
        max_count=max_q,
        optional=optional,
        is_group=is_group,
    )
