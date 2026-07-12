import pytest

from textfsm_ai.dsl.core.nodes import (
    AnyNode,
    ExactCountNode,
    LiteralNode,
    OneOrMoreNode,
    RangeQuantityNode,
    ZeroOrMoreNode,
    create_node,
)

DIGIT = r"[0-9]"
DIGITS = r"[0-9]+"


# ============================================================
# literal=True
# ============================================================


def test_create_node_literal_returns_literal_node():
    node = create_node("some literal text", literal=True)

    assert isinstance(node, LiteralNode)
    assert node.to_expression() == "some literal text"


# ============================================================
# range-<lo>-<hi>-<keyword>
# ============================================================


def test_create_node_range_finite():
    node = create_node("range-2-5-digit")

    assert isinstance(node, RangeQuantityNode)
    assert node.lo == 2
    assert node.hi == 5
    assert node.to_regex() == rf"{DIGIT}{{2,5}}"


def test_create_node_range_infinite_hi():
    node = create_node("range-1-inf-digit")

    assert isinstance(node, RangeQuantityNode)
    assert node.lo == 1
    assert node.hi is None
    assert node.to_regex() == rf"{DIGIT}{{1,}}"


def test_create_node_range_invalid_syntax_raises():
    with pytest.raises(ValueError, match="Invalid range syntax"):
        create_node("range-not-a-valid-range")


# ============================================================
# exact-<n>-<keyword>
# ============================================================


def test_create_node_exact_count():
    node = create_node("exact-3-digit")

    assert isinstance(node, ExactCountNode)
    assert node.count == 3
    assert node.to_regex() == rf"{DIGIT}{{3}}"


def test_create_node_exact_invalid_syntax_raises():
    with pytest.raises(ValueError, match="Invalid exact syntax"):
        create_node("exact-not-a-number-digit")


# ============================================================
# any-<keyword> -> zero-or-more
# ============================================================


def test_create_node_any_returns_zero_or_more_node():
    node = create_node("any-digit")

    assert isinstance(node, ZeroOrMoreNode)
    assert node.to_regex() == rf"{DIGIT}*"


# ============================================================
# some-<keyword> -> one-or-more
# ============================================================


def test_create_node_some_returns_one_or_more_node():
    node = create_node("some-digit")

    assert isinstance(node, OneOrMoreNode)
    assert node.to_regex() == rf"{DIGITS}"


# ============================================================
# Sanity: AnyNode/SomeNode classes exist but aren't wired into
# create_node's dispatch (any-/some- map to Zero/OneOrMoreNode
# instead) - not this file's concern, just confirming the import
# doesn't collide.
# ============================================================


def test_any_node_and_some_node_are_distinct_from_dispatch_result():
    dispatched = create_node("any-digit")
    assert not isinstance(dispatched, AnyNode)
