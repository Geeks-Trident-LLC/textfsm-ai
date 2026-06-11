import functools
import re
from dataclasses import dataclass
from typing import Optional

from textfsm_ai.core.serializable import Serializable
from textfsm_ai.dsl.aliases import ALIASES
from textfsm_ai.dsl.categories import BaseCategory
from textfsm_ai.dsl.nodes import base_keyword


@dataclass(frozen=True)
class KeywordExpression(Serializable):
    """
    Canonical semantic representation of a DSL keyword expression.
    """

    expression: str
    base: BaseCategory
    min_count: int = 1
    max_count: Optional[int] = None
    is_group: bool = False
    optional: bool = False
    varname: Optional[str] = None
    options: Optional[str] = None


EXPR_RE = re.compile(
    r"""
    ^(?P<prefix>
         optional-|
         maybe-|
         zero-or-more-|
         one-or-more-|
         some-|
         any-|
         not-|
         exact-\d+-|
         range-\d+-(?:\d+|inf)-
     )?
     (?P<keyword>[A-Za-z0-9_-]+)
     (?:\(
         (?P<args>[^)]*)
     \))?
    $
    """,
    re.VERBOSE,
)


def keyword_expression_from(expr: str) -> KeywordExpression:
    m = EXPR_RE.match(expr)
    if not m:
        raise ValueError(f"Invalid keyword expression: {expr}")

    prefix = m.group("prefix") or ""
    keyword = m.group("keyword")
    args = m.group("args") or ""

    # -----------------------------
    # Parse varname + options
    # -----------------------------
    varname = None
    options = None

    if args:
        parts = [p.strip() for p in args.split(",")]
        for p in parts:
            if p.startswith("var-"):
                varname = p[4:]
            elif p.startswith("options:"):
                options = p[len("options:") :]

    # -----------------------------
    # Determine base category
    # -----------------------------
    base = ALIASES.get(base_keyword(keyword), BaseCategory.WORD)

    min_count: int
    max_count: Optional[int]

    # exact-N-
    if prefix.startswith("exact-"):
        n = int(prefix.split("-")[1])
        min_count = max_count = n

    # range-lo-hi-
    elif prefix.startswith("range-"):
        parts = prefix[:-1].split("-")  # strip trailing '-'
        _, lo, hi = parts
        min_count = int(lo)
        max_count = None if hi == "inf" else int(hi)

    # zero-or-more- → 0..INF
    elif prefix.startswith("zero-or-more-"):
        min_count = 0
        max_count = None

    # one-or-more- → 1..INF
    elif prefix.startswith("one-or-more-"):
        min_count = 1
        max_count = None

    # some- → 1..INF
    elif prefix.startswith("some-"):
        min_count = 1
        max_count = None

    # any- → 0..INF
    elif prefix.startswith("any-"):
        min_count = 0
        max_count = None

    # not- → 0 tokens consumed (negative lookahead)
    elif prefix.startswith("not-"):
        min_count = 0
        max_count = 0

    # default → 1..1
    else:
        min_count = 1
        max_count = 1

    # -----------------------------
    # Determine counts + optional
    # -----------------------------
    optional = prefix.startswith(("optional-", "maybe-"))

    # group detection
    is_group = (min_count >= 2) or keyword.endswith("-group")

    return KeywordExpression(
        expression=expr,
        base=base,
        min_count=min_count,
        max_count=max_count,
        is_group=is_group,
        optional=optional,
        varname=varname,
        options=options,
    )


def wrap_keyword_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        expr_str = func(*args, **kwargs)
        return keyword_expression_from(expr_str)

    return wrapper
