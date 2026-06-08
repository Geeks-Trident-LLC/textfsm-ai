# textfsm_ai/dsl/pipeline.py

from textfsm_ai.dsl.ast_builder import build_ast_from_nodes
from textfsm_ai.dsl.expression_builder import sequence_to_expressions
from textfsm_ai.dsl.normalize import ExpressionNormalizer


def line_to_keyword_expressions(line: str, var_samples=None):
    normalizer = ExpressionNormalizer(var_samples)
    nodes = normalizer.normalize_to_nodes(line)
    seq = build_ast_from_nodes(nodes)
    return sequence_to_expressions(seq)
