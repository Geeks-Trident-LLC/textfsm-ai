# textfsm_ai/dsl/variable_infer.py

from collections import defaultdict

from textfsm_ai.dsl.core.patterns import PATTERNS
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword
from textfsm_ai.dsl.engine.parse.normalize import ExpressionNodeFactory


def infer_variable_mapping(records):
    values_by_var = defaultdict(list)

    for rec in records:
        for k, v in rec.items():
            if v:
                values_by_var[k.lower()].append(v)

    ExpressionNodeFactory()
    result = {}

    for varname, values in values_by_var.items():
        names = []

        for v in values:
            kw = infer_base_keyword([v])
            names.append(kw or "non-wss")

        keyword = max(set(names), key=names.count)
        pattern = PATTERNS[keyword].regex

        result[varname] = {
            "keyword": keyword,
            "dsl": f"{keyword}(var-{varname})",
            "regex": pattern,
        }

    return result
