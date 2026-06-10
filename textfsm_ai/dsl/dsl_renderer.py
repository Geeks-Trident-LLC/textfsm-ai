import re
from typing import Any, Dict, List

from textfsm_ai.generation.validator import TemplateValidator

CAPTURE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def render_dsl(dsl: Dict[str, Any], template_text: str, sample: str) -> str:
    """
    Render human-readable DSL aligned with:
    - TextFSM template indentation
    - literal spacing from sample text
    """

    if TemplateValidator.is_valid_template(template_text):
        raise ValueError(f"Invalid template\n{template_text}")

    var_lookup = {v["name"]: v for v in dsl["variables"]}
    rendered: List[str] = []

    for state in dsl["states"]:
        rendered.append(state["name"])

        for trans in state["transitions"]:
            pattern = trans["pattern"]
            action = trans["action"]

            # -------------------------
            # CASE 1: literal-only transition (no ${var})
            # -------------------------
            if "${" not in pattern:
                # Convert ^abc\s+xyz\s+123\s+connection:
                # into a real regex and match sample
                literal_regex = pattern.replace("\\s+", r"\s+")
                m = re.search(literal_regex, sample, re.MULTILINE)
                if not m:
                    raise ValueError(f"Literal pattern did not match sample: {pattern}")

                literal_text = m.group(0)

                tokens = ["  start() ", literal_text]
                if action:
                    tokens.append(" -> ")
                    tokens.append(action)

                rendered.append("".join(tokens))
                continue

            # -------------------------
            # CASE 2: variable transitions (existing logic)
            # -------------------------
            regex_parts = []
            pos = 0

            for m in CAPTURE_RE.finditer(pattern):
                varname = m.group(1)

                literal = pattern[pos : m.start()]
                if literal:
                    regex_parts.append(f"(?P<pre_{varname}>{literal})")

                vinfo = var_lookup[varname]
                regex_parts.append(f"(?P<{varname}>{vinfo['expression_regex']})")

                pos = m.end()

            tail = pattern[pos:]
            if tail:
                regex_parts.append(f"(?P<pre_tail>{tail})")

            full_regex = "".join(regex_parts)

            match = re.search(full_regex, sample, re.MULTILINE)
            if not match:
                raise ValueError(f"Pattern did not match sample: {pattern}")

            groups = match.groupdict()

            tokens: List[str] = []
            if pattern.startswith("^"):
                tokens.append("  start() ")

            for name, value in groups.items():
                if name.startswith("pre_"):
                    tokens.append(value)
                else:
                    tokens.append(var_lookup[name]["expression"])

            if action:
                tokens.append(" -> ")
                tokens.append(action)

            rendered.append("".join(tokens))

    return "\n".join(rendered)
