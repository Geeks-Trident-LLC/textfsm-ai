from collections import defaultdict
from typing import Dict, List

from textfsm_ai.dsl.ast.nodes import ValueNode
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword


def infer_call_keywords(values: List[ValueNode], records: List[dict]) -> Dict[str, str]:
    """
    Infer the keyword for each ValueNode based on sample records.

    Returns:
        { varname_lower: keyword }
    """
    samples = defaultdict(list)

    # Collect sample values for each variable
    for rec in records:
        for k, v in rec.items():
            if v:
                samples[k.lower()].append(v)

    result = {}

    for v in values:
        varname = v.name.lower()
        vals = samples.get(varname, [])

        if not vals:
            # No samples → fallback to broad optional keyword
            result[varname] = "optional-non-wss"
            continue

        # Infer keyword from sample values
        keyword = infer_base_keyword(vals)

        # Fallback to broad keyword
        if not keyword:
            keyword = "non-wss"

        result[varname] = keyword

    return result
