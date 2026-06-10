# tests/unit/dsl/test_custom_keyword_node.py

import pytest

from textfsm_ai.dsl.nodes import CustomKeywordNode, create_node


# -----------------------------
# basic mapping tests
# -----------------------------
@pytest.mark.parametrize(
    "kw,expected",
    [
        ("char", "."),
        ("any", ".*"),
        ("some", ".+"),
        ("ws", r"\s"),
        ("wss", r"\s+"),
        ("whitespace", r"\s"),
        ("whitespaces", r"\s+"),
    ],
)
def test_custom_keyword_regex(kw, expected):
    node = CustomKeywordNode(kw)
    assert node.regex == expected


# -----------------------------
# variable support
# -----------------------------
@pytest.mark.parametrize(
    "kw,expected",
    [
        ("char", "."),
        ("any", ".*"),
        ("some", ".+"),
    ],
)
def test_custom_keyword_with_varname(kw, expected):
    node = CustomKeywordNode(kw, varname="v0")
    assert node.to_regex(include_var=True) == f"(?P<v0>{expected})"
    assert node.to_regex(include_var=False) == expected


# -----------------------------
# generalization rules
# -----------------------------
@pytest.mark.parametrize(
    "kw,expected_name,expected_regex",
    [
        ("char", "any", ".*"),  # char → any
        ("ws", "wss", r"\s+"),  # ws → wss
        ("whitespace", "whitespaces", r"\s+"),  # whitespace → whitespaces
        ("any", "any", ".*"),  # idempotent
        ("some", "some", ".+"),  # idempotent
        ("wss", "wss", r"\s+"),  # idempotent
    ],
)
def test_custom_keyword_generalization(kw, expected_name, expected_regex):
    node = CustomKeywordNode(kw, generalize=True)
    assert node.name == expected_name
    assert node.regex == expected_regex


# -----------------------------
# expression rendering
# -----------------------------
def test_custom_keyword_expression_no_var():
    node = CustomKeywordNode("char")
    assert node.to_expression() == "char()"


def test_custom_keyword_expression_with_var():
    node = CustomKeywordNode("char", varname="v0")
    assert node.to_expression() == "char(var-v0)"


# -----------------------------
# error handling
# -----------------------------
def test_custom_keyword_invalid():
    with pytest.raises(ValueError):
        CustomKeywordNode("not-a-custom-keyword")


# -----------------------------
# integration: create_node()
# -----------------------------
@pytest.mark.parametrize(
    "kw,expected_cls",
    [
        ("char", CustomKeywordNode),
        ("any", CustomKeywordNode),
        ("some", CustomKeywordNode),
        ("ws", CustomKeywordNode),
        ("wss", CustomKeywordNode),
    ],
)
def test_create_node_custom_keywords(kw, expected_cls):
    node = create_node(kw)
    assert isinstance(node, expected_cls)
