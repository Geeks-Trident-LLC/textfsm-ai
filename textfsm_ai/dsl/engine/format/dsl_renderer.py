import re
from typing import List

from textfsm_ai.core.models import ReturnText
from textfsm_ai.core.utils.template import validate_template
from textfsm_ai.dsl.core.models import DSLExtractorResult
from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword

CAPTURE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def render_dsl(dsl: DSLExtractorResult, template: str, sample: str) -> ReturnText:
    """
    Render human-readable DSL aligned with:
    - TextFSM template indentation
    - literal spacing from sample text
    """

    validator = validate_template(template)
    if not validator.ready:
        return ReturnText(
            reason=f"Invalid template\n{validator.reason}\n{template}", ready=False
        )

    var_lookup = {v["name"]: v for v in dsl.variables or []}
    rendered: List[str] = []

    for state in dsl.states or []:
        rendered.append(state["name"])

        for trans in state["transitions"]:
            pattern = trans["pattern"] if isinstance(trans, dict) else trans
            action = trans["action"] if isinstance(trans, dict) else trans

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
                    return ReturnText(
                        reason=f"Literal pattern did not match sample: {pattern}",
                        ready=False,
                    )

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
                return ReturnText(
                    reason=f"Pattern did not match sample: {pattern}", ready=False
                )

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
    return ReturnText(return_text="\n".join(rendered), ready=True)


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
