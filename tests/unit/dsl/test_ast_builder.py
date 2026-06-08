# tests/test_ast_builder.py

from textfsm_ai.dsl.ast_builder import build_ast_from_nodes
from textfsm_ai.dsl.nodes import KeywordNode, LiteralNode, VariableKeywordNode


def test_build_ast_from_nodes():
    nodes = [
        LiteralNode("collected"),
        KeywordNode("digits"),
        VariableKeywordNode("digits", "v0"),
    ]
    seq = build_ast_from_nodes(nodes)
    assert [c.name for c in seq.items] == ["word", "digits", "digits"]
    assert [c.varname for c in seq.items] == [None, None, "v0"]
