# tests/unit/dsl/test_matcher.py

from textfsm_ai.dsl.matcher import expression_matches_tokens
from textfsm_ai.dsl.parser import parse_keyword_expression


def test_matcher_exact():
    expr = parse_keyword_expression("3-word")
    assert expression_matches_tokens(expr, ["a", "b", "c"])
    assert not expression_matches_tokens(expr, ["a", "b"])


def test_matcher_optional():
    expr = parse_keyword_expression("optional-2-word")
    assert expression_matches_tokens(expr, [])
    assert expression_matches_tokens(expr, ["a", "b"])
    assert not expression_matches_tokens(expr, ["a"])


def test_matcher_group():
    expr = parse_keyword_expression("word-group")
    assert expression_matches_tokens(expr, ["a", "b"])
    assert not expression_matches_tokens(expr, ["a"])
