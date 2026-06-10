# tests/test_normalize.py

from textfsm_ai.dsl.normalize import ExpressionNormalizer


def test_normalize_literal_line():
    norm = ExpressionNormalizer()
    line_expression = norm.normalize("collected 41 items")
    assert line_expression == "word() digits() word()"


def test_normalize_with_variable_and_samples():
    norm = ExpressionNormalizer({"v0": ["1", "2", "3"]})
    line_expresion = norm.normalize("collected ${v0} items")
    assert line_expresion == "word() digits(var-v0) word()"


def test_normalize_with_variable_no_samples():
    norm = ExpressionNormalizer()
    line_expression = norm.normalize("collected ${v0} items")
    assert line_expression == "word() any(var-v0) word()"
