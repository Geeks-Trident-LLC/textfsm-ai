# textfsm_ai/dsl/ast/pattern_pretty.py

from textfsm_ai.dsl.ast.nodes import PatternNode


def format_pattern(pattern: PatternNode) -> str:
    """
    Pretty-print a PatternNode for debugging.

    Uses each item's `expression` field to produce a human-friendly view.
    """
    parts = []
    for item in pattern.items:
        parts.append(item.expression)
    return " ".join(parts)


def format_pattern_textfsm(pattern: PatternNode) -> str:
    """
    Render a PatternNode back into a TextFSM-like pattern string.

    Uses each item's `textfsm_repr`.
    """
    parts = []
    for item in pattern.items:
        parts.append(item.textfsm_repr)
    return "".join(parts)
