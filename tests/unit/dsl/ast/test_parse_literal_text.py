# tests/test_parse_literal_text.py

from textfsm_ai.dsl.ast.nodes import (
    CallNode,
    LiteralNode,
    SpacerNode,
)
from textfsm_ai.dsl.ast.parser import parse_literal_text


def test_literal_simple():
    nodes = parse_literal_text("foo")
    assert len(nodes) == 1
    assert isinstance(nodes[0], LiteralNode)
    assert nodes[0].raw == "foo"


def test_literal_with_spaces():
    nodes = parse_literal_text("foo   bar")

    assert isinstance(nodes[0], LiteralNode)
    assert isinstance(nodes[1], SpacerNode)
    assert isinstance(nodes[2], LiteralNode)


def test_literal_with_puncts_group():
    # Assume PATTERNS["puncts-group"] matches "--"
    nodes = parse_literal_text("foo  . . . .    bar")

    assert isinstance(nodes[0], LiteralNode)
    assert isinstance(nodes[2], CallNode)  # puncts-group()
    assert isinstance(nodes[-1], LiteralNode)


def test_literal_with_digits():
    nodes = parse_literal_text("eth0")

    # Should infer keyword → create_node → CallNode
    assert len(nodes) == 1
    assert isinstance(nodes[0], CallNode)
    assert "var" not in nodes[0].expression.lower()  # not a VarNode
    assert nodes[0].raw == "eth0"


def test_literal_mixed():
    nodes = parse_literal_text("foo 123 ba . . . . baz")

    expects = [
        LiteralNode,
        SpacerNode,
        CallNode,
        SpacerNode,
        LiteralNode,
        SpacerNode,
        CallNode,
        SpacerNode,
        LiteralNode,
    ]

    for index, exp_cls in enumerate(expects):
        assert isinstance(nodes[index], exp_cls)
