# textfsm_ai/dsl/dsl_extractor.py

import re
from typing import Any, Optional

from textfsm_ai.dsl.nodes import create_node
from textfsm_ai.dsl.patterns import KEYWORD_TO_BASE, PATTERNS

VALUE_RE = re.compile(
    r"^Value"
    r"(?:\s+((?:Required|List|Key|Filldown|Fillup)"
    r"(?:,(?:Required|List|Key|Filldown|Fillup))*))?"
    r"\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"(\s+)\((.+)\)\s*$"
)

STATE_RE = re.compile(r"^(\w+)\s*$")
TRANSITION_RE = re.compile(r"^\s*(\^.+?)\s*(?:->\s*(.+))?$")


def extract_machine_dsl(canonical_template: str):
    lines = canonical_template.splitlines()

    variables = []
    states = []
    current_state: Optional[dict[str, Any]] = None

    for line in lines:
        m = VALUE_RE.match(line)
        if m:
            options, varname, ws, regex = m.groups()

            # reverse lookup keyword
            keyword = None
            for k, p in PATTERNS.items():
                if p.regex == regex:
                    keyword = k
                    break

            if keyword is None:
                raise ValueError(f"Unknown regex pattern: {regex!r}")

            node = create_node(keyword, varname, generalize=True)

            variables.append(
                {
                    "name": varname,
                    "keyword": keyword,
                    "category": KEYWORD_TO_BASE[keyword].name,
                    "options": options or "",
                    "expression": node.to_expression(),
                    "expression_regex": node.to_expression_regex(),
                }
            )

            continue

        # -------------------------
        # Parse state headers
        # -------------------------
        s = STATE_RE.match(line)
        if s:
            current_state = {"name": s.group(1), "transitions": []}
            states.append(current_state)
            continue

        # -------------------------
        # Parse transitions
        # -------------------------
        if current_state:
            t = TRANSITION_RE.match(line)
            if t:
                pattern, action = t.groups()
                current_state["transitions"].append(
                    {
                        "pattern": pattern,
                        "action": action or None,
                    }
                )

    return {
        "variables": variables,
        "states": states,
    }
