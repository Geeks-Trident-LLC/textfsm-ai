# tests/test_parse_body_pattern.py

import pytest

from textfsm_ai.dsl.ast.nodes import (
    LiteralNode,
    SpacerNode,
    ValueNode,
    VarNode,
)
from textfsm_ai.dsl.ast.parser import parse_body_pattern


@pytest.fixture
def v1_node():
    return VarNode(
        raw="${v1}",
        textfsm_repr="${v1}",
        expression="word(var-v1)",
        regex=r"\S+",
    )


@pytest.fixture
def values_by_name(v1_node):
    v = ValueNode(
        name="v1",
        regex=r"\S+",
        options=None,
        infer=v1_node,
    )
    return {"v1": v}


def test_body_with_single_var(values_by_name):

    body = "foo ${v1} bar"
    nodes = parse_body_pattern(body, values_by_name)

    assert len(nodes) == 5
    assert isinstance(nodes[0], LiteralNode)
    assert isinstance(nodes[1], SpacerNode)
    assert nodes[2] is values_by_name["v1"].infer
    assert isinstance(nodes[3], SpacerNode)
    assert isinstance(nodes[4], LiteralNode)


def test_body_with_parenthesized_var(values_by_name):
    body = "foo (${v1}) bar"
    nodes = parse_body_pattern(body, values_by_name)

    assert any(isinstance(n, VarNode) for n in nodes)
    assert nodes[2] is values_by_name["v1"].infer


def test_body_with_multiple_vars(values_by_name):
    body = "${v1} x ${v1}"
    nodes = parse_body_pattern(body, values_by_name)

    assert nodes[0] is values_by_name["v1"].infer
    assert isinstance(nodes[1], SpacerNode)
    assert isinstance(nodes[2], LiteralNode)
    assert nodes[-1] is values_by_name["v1"].infer
