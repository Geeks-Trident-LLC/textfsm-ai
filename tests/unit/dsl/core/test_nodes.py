# tests/unit/dsl/core/test_nodes.py

import re

from textfsm_ai.dsl.core.nodes import KeywordNode, LiteralNode, VariableKeywordNode


def test_literal_node_str():
    n = LiteralNode("collected")
    assert str(n) == "collected"
    assert n.to_expression() == "collected"


def test_literal_node_to_regex():
    n = LiteralNode("a.b")
    assert n.to_regex() == re.escape("a.b")


def test_keyword_node_str():
    n = KeywordNode("digits")
    assert str(n) == "digits()"
    assert n.to_expression() == "digits()"


def test_keyword_node_generalize_digit_to_digits():
    n = KeywordNode("digit", generalize=True)
    assert n.name == "digits"


def test_keyword_node_generalize_letter_to_word():
    n = KeywordNode("letter", generalize=True)
    assert n.name == "word"


def test_keyword_node_generalize_punct_to_puncts():
    n = KeywordNode("punct", generalize=True)
    assert n.name == "puncts"


def test_variable_keyword_node_str():
    n = VariableKeywordNode("digits", "v0")
    assert str(n) == "digits(var-v0)"
    assert n.to_expression() == "digits(var-v0)"


def test_variable_keyword_node_generalize_digit_to_digits():
    n = VariableKeywordNode("digit", "v0", generalize=True)
    assert n.name == "digits"


def test_variable_keyword_node_generalize_letter_to_word():
    n = VariableKeywordNode("letter", "v0", generalize=True)
    assert n.name == "word"


def test_variable_keyword_node_generalize_punct_to_puncts():
    n = VariableKeywordNode("punct", "v0", generalize=True)
    assert n.name == "puncts"


def test_variable_keyword_node_to_regex_include_var():
    n = VariableKeywordNode("digit", "v0")
    assert n.to_regex(include_var=True) == "(?P<v0>[0-9])"
    assert n.to_regex(include_var=False) == "[0-9]"
