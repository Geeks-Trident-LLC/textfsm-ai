# textfsm_ai/dsl/engine/render/template.py

from __future__ import annotations

from typing import List

from textfsm_ai.dsl.ast.nodes import (
    PatternNode,
    TemplateAST,
)


def render_template(ast: TemplateAST, canonicalized=True) -> str:
    """
    Render a canonical TextFSM template from a TemplateAST.
    This renderer is deterministic and round-trip safe.
    """

    parts: List[str] = []

    # ------------------------------------------------------------
    # 1. Render Value definitions
    # ------------------------------------------------------------
    for v in ast.values:
        opts = ""
        if v.options:
            opts = " " + ",".join(v.options)

        # canonicalized uses VarNode.textfsm_repr, not regex
        regex = v.infer.regex if canonicalized and v.infer is not None else v.regex
        parts.append(f"Value{opts} {v.name} ({regex})")

    # blank line after values
    if ast.values:
        parts.append("")

    # ------------------------------------------------------------
    # 2. Render states
    # ------------------------------------------------------------
    for state in ast.states:
        parts.append(state.name)

        for rule in state.rules:
            pat = _render_pattern(rule.pattern, canonicalized=canonicalized)
            act = _render_actions(rule.actions)
            parts.append(f"  {pat} -> {act}" if act else f"  {pat}")

        parts.append("")  # blank line after each state

    # remove trailing blank line
    while parts and parts[-1] == "":
        parts.pop()

    return "\n".join(parts)


# ------------------------------------------------------------
# Pattern rendering
# ------------------------------------------------------------


def _render_pattern(p: PatternNode, canonicalized=True) -> str:
    return "".join(item.textfsm_repr if canonicalized else item.raw for item in p.items)


# ------------------------------------------------------------
# Action rendering
# ------------------------------------------------------------


def _render_actions(actions):
    """
    Render list[Action] to canonical TextFSM action expression.
    TextFSM only supports one action per rule in your engine.
    """
    if not actions:
        return ""

    a = actions[0]

    # EOF
    if a.eof_action:
        return "EOF"

    # Error
    if a.error_pattern:
        return f"Error {a.error_pattern}"

    # Combined: Next.Record Foo
    if a.line_action and a.record_action:
        if a.state:
            return f"{a.line_action}.{a.record_action} {a.state}"
        return f"{a.line_action}.{a.record_action}"

    # Line-only: Next Foo
    if a.line_action:
        if a.state:
            return f"{a.line_action} {a.state}"
        return a.line_action

    # Record-only: Record Foo
    if a.record_action:
        if a.state:
            return f"{a.record_action} {a.state}"
        return a.record_action

    if a.state:
        return a.state

    raise ValueError(f"Cannot render action: {a}")
