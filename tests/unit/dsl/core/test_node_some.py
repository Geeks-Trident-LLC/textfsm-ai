# tests/unit/dsl/core/test_node_some.py

from textfsm_ai.dsl.core.nodes import SomeNode, create_node

WORD = "[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"
WSS = r"\s+"


def test_some_word():
    node = SomeNode(create_node("word"))
    assert node.to_regex() == rf"{WORD}(?:{WSS}{WORD})*"


def test_some_word_item():
    node = SomeNode(create_node("word-item"))
    assert node.to_regex() == rf"{WORD}(?:{WSS}{WORD})*"


def test_some_word_group():
    node = SomeNode(create_node("word-group"))
    assert node.to_regex() == rf"{WORD}(?:{WSS}{WORD})+"


def test_some_atomic():
    node = SomeNode(create_node("digit"))
    assert node.to_regex() == "[0-9]+"


def test_some_atomic_plus():
    node = SomeNode(create_node("digits"))
    assert node.to_regex() == "[0-9]+"
