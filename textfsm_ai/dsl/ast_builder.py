# textfsm_ai/dsl/ast_builder.py

from textfsm_ai.dsl.ast import KeywordCall, SequenceExpression
from textfsm_ai.dsl.nodes import (
    BaseNode,
    CustomKeywordNode,
    KeywordNode,
    LiteralNode,
    VariableKeywordNode,
)


def build_ast_from_nodes(nodes: list[BaseNode]) -> SequenceExpression:
    items: list[KeywordCall] = []

    for node in nodes:
        if isinstance(node, LiteralNode):
            # treat literal as a "word" keyword
            items.append(KeywordCall(name="word", varname=None))
        elif isinstance(node, KeywordNode):
            items.append(KeywordCall(name=node.keyword, varname=None))
        elif isinstance(node, VariableKeywordNode):
            items.append(KeywordCall(name=node.keyword, varname=node.varname))
        elif isinstance(node, CustomKeywordNode):
            items.append(KeywordCall(name=node.keyword, varname=node.varname))
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

    return SequenceExpression(items=items)
