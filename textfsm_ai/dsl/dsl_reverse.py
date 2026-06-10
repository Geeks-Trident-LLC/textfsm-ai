# textfsm_ai/dsl/dsl_reverse.py

import re
from typing import Any, Dict, List

KEYWORD_TO_REGEX = {
    "digits": r"[0-9]+",
    "mixed-word": r"[!-~]*[0-9A-Za-z][!-~]*",
    "non-wss": r"\S+",
    "word": r"[A-Za-z]+",
    "char": r".",
    "any": r".*",
    "some": r".+",
}


VAR_CALL_RE = re.compile(r"^([A-Za-z0-9_-]+)\(var-([A-Za-z_][A-Za-z0-9_]*)\)$")


def dsl_to_canonical(dsl: Dict[str, Any]) -> str:
    """
    Convert machine-readable DSL back into canonical TextFSM template.
    """

    lines: List[str] = []

    # -------------------------
    # Value definitions
    # -------------------------
    for v in dsl["variables"]:
        regex = KEYWORD_TO_REGEX.get(v["keyword"], r"\S+")
        lines.append(f"Value {v['name']} ({regex})")

    # -------------------------
    # States
    # -------------------------
    for state in dsl["states"]:
        lines.append(state["name"])

        for trans in state["transitions"]:
            pattern = trans["pattern"]
            action = trans["action"]

            # Replace ${var} with capture groups
            def repl(m):
                varname = m.group(1)
                v = next(v for v in dsl["variables"] if v["name"] == varname)
                regex = KEYWORD_TO_REGEX.get(v["keyword"], r"\S+")
                return f"({regex})"

            rebuilt = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, pattern)

            if action:
                lines.append(f"  {rebuilt} -> {action}")
            else:
                lines.append(f"  {rebuilt}")

    return "\n".join(lines)
