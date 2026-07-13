# tests/unit/dsl/core/test_node_any.py

from textfsm_ai.dsl.core.nodes import AnyNode, create_node

WORD = "[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"
WSS = r"\s+"


def test_any_word():
    node = AnyNode(create_node("word"))
    assert node.to_regex() == f"(?:{WORD})?"


def test_any_word_item():
    node = AnyNode(create_node("word-item"))
    assert node.to_regex() == f"(?:{WORD}(?:{WSS}{WORD})*)?"


def test_any_word_group():
    node = AnyNode(create_node("word-group"))
    assert node.to_regex() == f"(?:{WORD}(?:{WSS}{WORD})+)?"


def test_any_atomic():
    node = AnyNode(create_node("digit"))
    assert node.to_regex() == "[0-9]?"


def test_any_atomic_plus():
    node = AnyNode(create_node("digits"))
    assert node.to_regex() == "[0-9]*"


def test_any_to_expression():
    node = AnyNode(create_node("digit"))
    assert node.to_expression() == "any-digit()"
