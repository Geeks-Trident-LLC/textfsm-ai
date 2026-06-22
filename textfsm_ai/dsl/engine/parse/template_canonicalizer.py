# textfsm_ai/dsl/template_canonicalizer.py

import re
from typing import List

from textfsm_ai.core.models import ReturnText
from textfsm_ai.core.utils.template import validate_template

from .variable_infer import infer_variable_mapping

VALUE_LINE_RE = re.compile(
    r"^Value"
    r"(?:\s+(\w+(?:,\w+)*))?"  # options (optional)
    r"\s+([A-Za-z_][A-Za-z0-9_]*)"  # variable name
    r"\s*\((.+)\)\s*$"  # regex
)


def canonicalize(llm_template: str, records: List[dict]) -> ReturnText:
    var_mapping = infer_variable_mapping(records)
    lines = llm_template.splitlines()
    out = []

    for line in lines:
        m = VALUE_LINE_RE.match(line)
        if not m:
            out.append(line)
            continue

        options, varname, _old_regex = m.groups()

        # normalize variable name
        varname = varname.lower()

        info = var_mapping.get(varname)
        if not info:
            out.append(line)
            continue

        # normalize options
        if options:
            opts = sorted(options.split(","))
            opt_str = ",".join(opts)
            out.append(f"Value {opt_str} {varname} ({info['regex']})")
        else:
            out.append(f"Value {varname} ({info['regex']})")

    template = "\n".join(out)
    validator = validate_template(template)

    if not validator.ready:
        return ReturnText(return_text=template, reason=validator.reason, ready=False)

    return ReturnText(return_text=template, ready=True)
