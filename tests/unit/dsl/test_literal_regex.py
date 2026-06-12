import re

from textfsm_ai.dsl.dsl_recognizer import _build_literal_regex
from textfsm_ai.dsl.patterns import PATTERNS_MAPPING

PUNCTS_GROUP = PATTERNS_MAPPING["puncts-group"]
DIGITS = PATTERNS_MAPPING["digits"]
NUMBER = PATTERNS_MAPPING.get("number", r"\S+")


# ------------------------------------------------------------
# Basic whitespace handling
# ------------------------------------------------------------


def test_literal_whitespace_single_space():
    assert _build_literal_regex(" ") == r"\s+"


def test_literal_whitespace_multiple_spaces():
    assert _build_literal_regex("   ") == r"\s+"


def test_literal_literal_s_plus():
    assert _build_literal_regex(r"\s+") == r"\s+"


# ------------------------------------------------------------
# Word / letter / mixed-word handling
# ------------------------------------------------------------


def test_literal_word():
    assert _build_literal_regex("abc") == r"abc"


def test_literal_mixed_word_no_digits():
    assert _build_literal_regex("Gi") == r"Gi"


def test_literal_word_with_digits_should_not_escape_as_word():
    # "Gi0" contains digits → NUMBER
    assert _build_literal_regex("Gi0") == "[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"


# ------------------------------------------------------------
# Punctuation handling
# ------------------------------------------------------------


def test_literal_single_punct():
    assert _build_literal_regex(".") == r"\."


def test_literal_multi_punct():
    assert _build_literal_regex("...") == r"\.\.\."


# ------------------------------------------------------------
# Puncts-group recursion
# ------------------------------------------------------------


def test_literal_puncts_group_sequence():
    txt = ". . . . ."
    out = _build_literal_regex(txt)
    assert out == PUNCTS_GROUP


def test_literal_puncts_group_with_prefix_suffix():
    txt = "abc . . . . . xyz"
    out = _build_literal_regex(txt)
    assert out == rf"abc\s+{PUNCTS_GROUP}\s+xyz"


# ------------------------------------------------------------
# Digits → NUMBER
# ------------------------------------------------------------


def test_literal_digits():
    assert _build_literal_regex("123") == NUMBER


def test_literal_digits_mixed():
    assert _build_literal_regex("1500") == NUMBER


# ------------------------------------------------------------
# Mixed tokens
# ------------------------------------------------------------


def test_literal_mixed_tokens():
    txt = "abc   . . .   123"
    out = _build_literal_regex(txt)
    assert "abc" in out
    assert PUNCTS_GROUP in out
    assert NUMBER in out
    assert r"\s+" in out


# ------------------------------------------------------------
# Fallback behavior
# ------------------------------------------------------------


def test_literal_fallback_non_whitespace():
    txt = "@@@"
    out = _build_literal_regex(txt)
    assert out == re.escape("@@@")
