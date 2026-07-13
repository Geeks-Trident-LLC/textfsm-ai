# tests/unit/dsl/engine/parse/test_infer.py

import pytest

from textfsm_ai.dsl.core.categories import BaseCategory
from textfsm_ai.dsl.engine.parse.infer import infer_base_category, infer_base_keyword


@pytest.mark.parametrize(
    "tokens, expected_keyword, expected_category",
    [
        # word
        (["abc"], "word", BaseCategory.WORD),
        (["xyz"], "word", BaseCategory.WORD),
        (["abc", "xyz"], "word", BaseCategory.WORD),
        # word-group
        (["abc xyz"], "word-group", BaseCategory.WORD),
        # words (multi-token mixed)
        (["abc xyz", "def"], "words", BaseCategory.WORD),
        # number
        (["123"], "digits", BaseCategory.DIGIT),
        (["0.1"], "number", BaseCategory.NUMBER),
        ([".1"], "number", BaseCategory.NUMBER),
        (["1."], "number", BaseCategory.NUMBER),
        # mixed-number
        (["+2.2"], "mixed-number", BaseCategory.MIXED_NUMBER),
        (["(2.2)"], "mixed-number", BaseCategory.MIXED_NUMBER),
        (["1,200.50"], "mixed-number", BaseCategory.MIXED_NUMBER),
    ],
)
def test_infer(tokens, expected_keyword, expected_category):
    kw = infer_base_keyword(tokens)
    cat = infer_base_category(tokens)

    assert kw == expected_keyword
    assert cat == expected_category


def test_infer_base_keyword_accepts_single_string_not_just_a_list():
    assert infer_base_keyword("abc") == "word"


def test_infer_base_keyword_returns_none_when_all_tokens_are_empty():
    assert infer_base_keyword(["", ""]) is None


def test_infer_base_keyword_returns_none_when_no_pattern_matches():
    # A whitespace-only token matches no registered pattern at all
    # (every pattern requires at least one non-whitespace char).
    assert infer_base_keyword([" "]) is None


def test_infer_base_category_returns_none_when_keyword_is_none():
    assert infer_base_category([" "]) is None
