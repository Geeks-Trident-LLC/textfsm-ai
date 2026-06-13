# textfsm_ai/dsl/expression_builder.py

from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.engine.format.expression import (
    KeywordExpression,
    keyword_expression_from,
)


def keyword_call_to_expression(call) -> KeywordExpression:
    """
    Convert a KeywordCall into a KeywordExpression by routing through
    the node system. This ensures consistent handling of generalization,
    grouping, and variable semantics.
    """
    node = create_node(call.name, call.varname, generalize=True)
    return keyword_expression_from(node.to_expression())


def sequence_to_expressions(seq) -> list[KeywordExpression]:
    """
    Convert a SequenceExpression (or any object with .items) into a list
    of KeywordExpressions.
    """
    return [keyword_call_to_expression(c) for c in seq.items]
