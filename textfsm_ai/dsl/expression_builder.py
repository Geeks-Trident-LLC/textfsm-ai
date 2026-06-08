# textfsm_ai/dsl/expression_builder.py

from textfsm_ai.dsl.ast import KeywordCall
from textfsm_ai.dsl.expression import KeywordExpression
from textfsm_ai.dsl.patterns import KEYWORD_TO_BASE


def keyword_call_to_expression(call: KeywordCall) -> KeywordExpression:
    base = KEYWORD_TO_BASE.get(call.name)
    if base is None:
        raise ValueError(f"Unknown keyword: {call.name}")

    return KeywordExpression(
        base=base,
        min_count=1,
        max_count=1,
        optional=False,
        is_group=False,
        varname=call.varname,
    )


def sequence_to_expressions(seq) -> list[KeywordExpression]:
    return [keyword_call_to_expression(c) for c in seq.items]
