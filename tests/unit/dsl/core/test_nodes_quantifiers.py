# tests/unit/dsl/core/test_nodes_quantifiers.py

import pytest

from textfsm_ai.dsl.core.nodes import create_node

# ------------------------------------------------------------
# Expected base patterns (must match patterns.py)
# ------------------------------------------------------------

DIGIT = r"[0-9]"
DIGITS = r"[0-9]+"
WORD = r"[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"
WORD_ITEM = rf"{WORD}(?:\s+{WORD})*"
WORD_GROUP = rf"{WORD}(?:\s+{WORD})+"

# ------------------------------------------------------------
# optional-
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("optional-digit", rf"{DIGIT}?"),
        ("optional-word-item", rf"(?:{WORD_ITEM})?"),
    ],
)
def test_optional(keyword, expected):
    node = create_node(keyword)
    assert node.to_regex() == expected


# ------------------------------------------------------------
# maybe- (alias of optional-)
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("maybe-word", rf"(?:{WORD})?"),
    ],
)
def test_maybe(keyword, expected):
    node = create_node(keyword)
    assert node.to_regex() == expected


# ------------------------------------------------------------
# zero-or-more-
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("zero-or-more-digit", rf"{DIGIT}*"),
        ("zero-or-more-digits", rf"{DIGIT}*"),
        ("zero-or-more-word", rf"(?:{WORD_ITEM})*"),
        ("zero-or-more-word-item", rf"(?:{WORD_ITEM})*"),
        ("zero-or-more-word-group", rf"(?:{WORD_GROUP})*"),
    ],
)
def test_zero_or_more(keyword, expected):
    node = create_node(keyword)
    assert node.to_regex() == expected


def test_zero_or_more_to_expression():
    node = create_node("zero-or-more-digit")
    assert node.to_expression() == "zero_or_more-digit()"


def test_one_or_more_to_expression():
    node = create_node("one-or-more-digit")
    assert node.to_expression() == "one_or_more-digit()"


# ------------------------------------------------------------
# one-or-more-
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("one-or-more-digit", rf"{DIGITS}"),
        ("one-or-more-digits", rf"{DIGITS}"),
        ("one-or-more-word", rf"{WORD_ITEM}"),
        ("one-or-more-word-item", rf"{WORD_ITEM}"),
    ],
)
def test_one_or_more(keyword, expected):
    node = create_node(keyword)
    assert node.to_regex() == expected


# ------------------------------------------------------------
# not-
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("not-digit", rf"(?!{DIGIT})"),
        ("not-word", rf"(?!{WORD})"),
    ],
)
def test_not(keyword, expected):
    node = create_node(keyword)
    assert node.to_regex() == expected
