# tests/unit/dsl/core/test_nodes.py

from textfsm_ai.dsl.core.nodes import KeywordNode, LiteralNode, VariableKeywordNode


def test_literal_node_str():
    n = LiteralNode("collected")
    assert str(n) == "collected"
    assert n.to_expression() == "collected"


def test_keyword_node_str():
    n = KeywordNode("digits")
    assert str(n) == "digits()"
    assert n.to_expression() == "digits()"


def test_variable_keyword_node_str():
    n = VariableKeywordNode("digits", "v0")
    assert str(n) == "digits(var-v0)"
    assert n.to_expression() == "digits(var-v0)"
