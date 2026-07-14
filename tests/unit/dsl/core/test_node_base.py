# tests/unit/dsl/core/test_node_base.py

import pytest

from textfsm_ai.dsl.core.nodes import BaseNode


def test_base_node_is_instantiable():
    node = BaseNode()
    assert callable(node.to_regex)
    assert callable(node.to_expression)
    assert "base.BaseNode" in repr(node)


def test_base_node_to_regex_raises_not_implemented():
    node = BaseNode()
    with pytest.raises(NotImplementedError):
        node.to_regex()


def test_base_node_to_expression_raises_not_implemented():
    node = BaseNode()
    with pytest.raises(NotImplementedError):
        node.to_expression()


def test_base_node_str_raises_not_implemented():
    # __str__ delegates to to_expression(), which is itself unimplemented.
    node = BaseNode()
    with pytest.raises(NotImplementedError):
        str(node)
