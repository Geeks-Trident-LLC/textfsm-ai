# textfsm_ai/dsl/template_canonicalizer.py

import re

from .variable_infer import infer_variable_mapping

# Matches:
#   Value interface (...)
#   Value Required interface (...)
#   Value Optional interface (...)
VALUE_LINE_RE = re.compile(
    r"^(Value)(?:\s+(Required|Optional))?\s+([A-Za-z_][A-Za-z0-9_]*)(\s+)\((.+)\)\s*$"
)


class TemplateCanonicalizer:
    def canonicalize(self, template: str, records):
        var_mapping = infer_variable_mapping(records)
        lines = template.splitlines()
        out = []

        for line in lines:
            m = VALUE_LINE_RE.match(line)
            if not m:
                out.append(line)
                continue

            value_kw, req_opt, varname, ws, _old = m.groups()
            info = var_mapping.get(varname)

            if not info:
                out.append(line)
                continue

            # Preserve Required/Optional if present
            if req_opt:
                out.append(f"{value_kw} {req_opt} {varname}{ws}({info['regex']})")
            else:
                out.append(f"{value_kw} {varname}{ws}({info['regex']})")

        return "\n".join(out)
