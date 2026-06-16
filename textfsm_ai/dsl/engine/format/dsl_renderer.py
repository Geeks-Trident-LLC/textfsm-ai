import re
from typing import Any, Dict, List

from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword
from textfsm_ai.generation.support.validator import TemplateValidator

CAPTURE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def render_dsl(ast: Dict[str, Any], template: str, sample: str) -> str:
    """
    Render human-readable DSL aligned with:
    - TextFSM template indentation
    - literal spacing from sample text
    """

    if not TemplateValidator.is_valid_template(template):
        raise ValueError(f"Invalid template\n{template}")

    var_lookup = {v["name"]: v for v in ast["variables"]}
    rendered: List[str] = []

    for state in ast["states"]:
        rendered.append(state["name"])

        for trans in state["transitions"]:
            pattern = trans["pattern"]
            action = trans["action"]

            # NEW: detect end-of-line marker
            has_end = pattern.endswith("$$")
            if has_end:
                pattern = pattern[:-2]  # strip "$$"

            # -------------------------
            # CASE 1: literal-only transition
            # -------------------------
            if "${" not in pattern:
                literal_regex = pattern.replace("\\s+", r"\s+")
                m = re.search(literal_regex, sample, re.MULTILINE)
                if not m:
                    raise ValueError(f"Literal pattern did not match sample: {pattern}")

                literal_text = render_literal_text(m.group(0))

                tokens = ["  start() ", literal_text]

                if has_end:
                    tokens.append(" end()")  # NEW

                if action:
                    tokens.append(" -> ")
                    tokens.append(action)

                rendered.append("".join(tokens))
                continue

            # -------------------------
            # CASE 2: variable transitions
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

            tokens = []
            if pattern.startswith("^"):
                tokens.append("  start() ")

            for name, value in groups.items():
                if name.startswith("pre_"):
                    tokens.append(value)
                else:
                    tokens.append(var_lookup[name]["expression"])

            if has_end:
                tokens.append(" end()")  # NEW

            if action:
                tokens.append(" -> ")
                tokens.append(action)

            rendered.append("".join(tokens))

    return "\n".join(rendered)


TOKEN_RE = re.compile(r"(\s+|[^\s]+)")


def render_literal_text(literal_text: str) -> str:
    """
    Convert literal sample text into DSL-friendly literal text:
    - preserve all spacers
    - infer keyword for each token
    - convert token → DSL expression when appropriate
    """

    parts = []
    tokens = TOKEN_RE.findall(literal_text)

    for tok in tokens:
        # 1. Spacers preserved exactly
        if tok.isspace():
            parts.append(tok)
            continue

        # 2. Infer keyword
        keyword = infer_base_keyword([tok])

        # 3. word / letter → literal node
        if keyword in ("word", "letter"):
            if re.search("[0-9]", tok):
                node = create_node(keyword, generalize=True)
            else:
                node = create_node(tok, literal=True)
            parts.append(node.to_expression())
            continue

        # 5. mixed-word
        if keyword == "mixed-word":
            # Try literal-safe
            if not re.search("[0-9]", tok):
                node = create_node(tok, literal=True)
                parts.append(node.to_expression())
            else:
                parts.append("mixed-word()")
            continue

        # 6. punct / puncts
        if keyword in ("punct", "puncts", "puncts-item", "puncts-group"):
            node = create_node(tok, literal=True)
            parts.append(node.to_expression())
            continue

        # 7. fallback: generalized keyword
        node = create_node(keyword, generalize=True)
        parts.append(node.to_expression())

    return "".join(parts)
