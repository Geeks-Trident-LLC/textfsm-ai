import re
from typing import Optional

from .base import BaseNode
from .leaf import (
    CustomKeywordNode,
    KeywordNode,
    LiteralNode,
    VariableKeywordNode,
    check_custom_keyword,
)
from .modifiers import NotNode, OptionalNode
from .quantifiers import (
    ExactCountNode,
    OneOrMoreNode,
    RangeQuantityNode,
    ZeroOrMoreNode,
)

# ------------------------------------------------------------
# Node Factory
# ------------------------------------------------------------


def create_node(
    keyword: str,
    varname: Optional[str] = None,
    extra: str = "",
    generalize: bool = False,
    literal: bool = False,
) -> BaseNode:
    if literal:
        return LiteralNode(keyword)

    if check_custom_keyword(keyword):
        return CustomKeywordNode(
            keyword, varname=varname, extra=extra, generalize=generalize
        )

    # ------------------------------------------------------------
    # range-lo-hi-keyword
    # range-lo-inf-keyword
    # ------------------------------------------------------------
    if keyword.startswith("range-"):
        # pattern: range-<lo>-<hi>-<keyword>
        m = re.match(r"range-(\d+)-(inf|\d+)-(.+)", keyword)
        if not m:
            raise ValueError(f"Invalid range syntax: {keyword}")

        lo = int(m.group(1))
        hi_raw = m.group(2)
        hi = None if hi_raw == "inf" else int(hi_raw)
        inner_kw = m.group(3)

        inner_node = create_node(inner_kw, varname, extra, generalize)
        return RangeQuantityNode(inner_node, lo, hi)

    # ------------------------------------------------------------
    # exact-n-keyword
    # ------------------------------------------------------------
    if keyword.startswith("exact-"):
        # pattern: exact-<n>-<keyword>
        m = re.match(r"exact-(\d+)-(.+)", keyword)
        if not m:
            raise ValueError(f"Invalid exact syntax: {keyword}")

        count = int(m.group(1))
        inner_kw = m.group(2)

        inner_node = create_node(inner_kw, varname, extra, generalize)
        return ExactCountNode(inner_node, count)

    # ------------------------------------------------------------
    # any-<keyword>  → zero-or-more
    # ------------------------------------------------------------
    if keyword.startswith("any-"):
        inner_kw = keyword[len("any-") :]
        return ZeroOrMoreNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # some-<keyword> → one-or-more
    # ------------------------------------------------------------
    if keyword.startswith("some-"):
        inner_kw = keyword[len("some-") :]
        return OneOrMoreNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # maybe-<keyword> → optional
    # ------------------------------------------------------------
    if keyword.startswith("maybe-"):
        inner_kw = keyword[len("maybe-") :]
        return OptionalNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # optional-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("optional-"):
        inner_kw = keyword[len("optional-") :]
        return OptionalNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # zero-or-more-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("zero-or-more-"):
        inner_kw = keyword[len("zero-or-more-") :]
        return ZeroOrMoreNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # one-or-more-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("one-or-more-"):
        inner_kw = keyword[len("one-or-more-") :]
        return OneOrMoreNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # not-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("not-"):
        inner_kw = keyword[len("not-") :]
        return NotNode(create_node(inner_kw, varname, extra, generalize))

    # ------------------------------------------------------------
    # variable keyword
    # ------------------------------------------------------------
    if varname is not None:
        return VariableKeywordNode(keyword, varname, extra, generalize)

    # ------------------------------------------------------------
    # plain keyword
    # ------------------------------------------------------------
    return KeywordNode(keyword, generalize)
