# tests/unit/dsl/test_exact_count_node.py

from textfsm_ai.dsl.categories import BaseCategory
from textfsm_ai.dsl.expression import KeywordExpression


def test_expression_model():
    expr = KeywordExpression(
        base=BaseCategory.WORD,
        min_count=2,
        max_count=3,
        optional=True,
        is_group=True,
    )
    assert expr.base == BaseCategory.WORD
    assert expr.min_count == 2
    assert expr.max_count == 3
    assert expr.optional
    assert expr.is_group
