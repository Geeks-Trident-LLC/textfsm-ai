# tests/unit/dsl/core/test_node_modifiers.py

from textfsm_ai.dsl.core.nodes import MaybeNode, create_node

DIGIT = r"[0-9]"
DIGITS = r"[0-9]+"
WORD = r"[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"


# ---------------------------------------------------------
# OptionalNode
# ---------------------------------------------------------
def test_optional_atomic_plus():
    node = create_node("optional-digits")
    assert node.to_regex() == f"{DIGIT}*"


def test_optional_to_expression():
    node = create_node("optional-digit")
    assert node.to_expression() == "optional-digit()"


# ---------------------------------------------------------
# MaybeNode (not wired into create_node's dispatch - "maybe-" maps to
# OptionalNode instead - but the class itself is still part of the
# public API, so it needs its own direct coverage).
# ---------------------------------------------------------
def test_maybe_node_to_regex_behaves_like_optional():
    node = MaybeNode(create_node("word"))
    assert node.to_regex() == f"(?:{WORD})?"


def test_maybe_node_to_expression():
    node = MaybeNode(create_node("digit"))
    assert node.to_expression() == "maybe-digit()"


# ---------------------------------------------------------
# NotNode
# ---------------------------------------------------------
def test_not_to_expression():
    node = create_node("not-digit")
    assert node.to_expression() == "not-digit()"
