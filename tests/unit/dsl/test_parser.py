# tests/unit/dsl/test_parser.py

import pytest

from textfsm_ai.dsl.categories import BaseCategory
from textfsm_ai.dsl.parser import parse_keyword_expression


def test_parse_simple_word():
    expr = parse_keyword_expression("word")
    assert expr.base == BaseCategory.WORD
    assert expr.min_count == 1
    assert expr.max_count == 1
    assert not expr.optional


def test_parse_plural_words():
    expr = parse_keyword_expression("words")
    assert expr.base == BaseCategory.WORD
    assert expr.min_count == 1
    assert expr.max_count is None


def test_parse_exact_quantity():
    expr = parse_keyword_expression("3-word")
    assert expr.base == BaseCategory.WORD
    assert expr.min_count == 3
    assert expr.max_count == 3


def test_parse_range_quantity():
    expr = parse_keyword_expression("2-to-4-word")
    assert expr.min_count == 2
    assert expr.max_count == 4


def test_parse_optional_quantity_normalized():
    expr = parse_keyword_expression("optional-3-word")
    assert expr.optional
    assert expr.min_count == 3
    assert expr.max_count == 3


def test_parse_item_suffix():
    expr = parse_keyword_expression("word-item")
    assert expr.base == BaseCategory.WORD
    assert not expr.is_group


def test_parse_group_suffix():
    expr = parse_keyword_expression("word-group")
    assert expr.is_group


def test_parse_unknown_keyword():
    with pytest.raises(ValueError):
        parse_keyword_expression("unknown")
