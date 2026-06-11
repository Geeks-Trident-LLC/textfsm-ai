# tests/unit/dsl/test_expression.py

import json

import pytest

from textfsm_ai.dsl.categories import BaseCategory
from textfsm_ai.dsl.expression import (
    KeywordExpression,
    keyword_expression_from,
)

# ------------------------------------------------------------
# Basic construction + serialization
# ------------------------------------------------------------


def test_keyword_expression_to_dict_and_json():
    expr = KeywordExpression(
        expression="word(var-x)",
        base=BaseCategory.WORD,
        min_count=1,
        max_count=1,
        is_group=False,
        optional=False,
        varname="x",
        options=None,
    )
    d = expr.to_dict()
    assert d["expression"] == "word(var-x)"
    assert d["base"] == BaseCategory.WORD.name
    assert d["varname"] == "x"

    j = expr.to_json()
    parsed = json.loads(j)
    assert parsed["expression"] == "word(var-x)"
    assert parsed["varname"] == "x"


def test_keyword_expression_from_dict_roundtrip():
    original = KeywordExpression(
        expression="word(var-y)",
        base=BaseCategory.WORD,
        min_count=1,
        max_count=1,
        is_group=False,
        optional=False,
        varname="y",
        options=None,
    )

    d = original.to_dict()
    restored = KeywordExpression.from_dict(d)

    assert restored == original


# ------------------------------------------------------------
# Prefix parsing
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, min_count, max_count, optional",
    [
        ("optional-word()", 1, 1, True),
        ("maybe-word()", 1, 1, True),
        ("zero-or-more-word()", 0, None, False),
        ("one-or-more-word()", 1, None, False),
        ("some-word()", 1, None, False),
        ("any-word()", 0, None, False),
        ("exact-3-word()", 3, 3, False),
        ("range-2-5-word()", 2, 5, False),
        ("range-1-inf-word()", 1, None, False),
        ("not-word()", 0, 0, False),
    ],
)
def test_prefix_parsing(expr, min_count, max_count, optional):
    k = keyword_expression_from(expr)
    assert k.min_count == min_count
    assert k.max_count == max_count
    assert k.optional == optional


# ------------------------------------------------------------
# Varname + options parsing
# ------------------------------------------------------------


def test_varname_and_options_parsing():
    expr = "word(var-iface, options:List)"
    k = keyword_expression_from(expr)

    assert k.varname == "iface"
    assert k.options == "List"


# ------------------------------------------------------------
# Base category inference
# ------------------------------------------------------------


def test_base_category_inference():
    k = keyword_expression_from("word()")
    assert k.base == BaseCategory.WORD

    k2 = keyword_expression_from("mixed-word()")
    assert k2.base == BaseCategory.MIXED_WORD


# ------------------------------------------------------------
# Group detection
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("word()", False),
        ("word-group()", True),
        ("range-2-5-word()", True),
        ("exact-3-word()", True),
        ("some-word()", False),  # 1..∞ is NOT a group
        ("one-or-more-word()", False),  # 1..∞ is NOT a group
    ],
)
def test_group_detection(expr, expected):
    k = keyword_expression_from(expr)
    assert k.is_group == expected
