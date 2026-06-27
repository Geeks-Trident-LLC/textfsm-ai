# textfsm_ai/dsl/engine/render/readable.py

from __future__ import annotations

from typing import List

from textfsm_ai.dsl.ast.nodes import (
    PatternNode,
    SpacerNode,
    TemplateAST,
)


def render_readable(ast: TemplateAST) -> str:
    """
    Render a human-readable DSL from a TemplateAST.
    This is NOT TextFSM — this is your pretty DSL.
    """

    parts: List[str] = []

    for state in ast.states:
        parts.append(f"state {state.name}:")
        for rule in state.rules:
            pat = _render_pattern_readable(rule.pattern)
            act = _render_action_readable(rule.actions)
            parts.append(f"  {pat} -> {act}" if act else f"  {pat}")
        parts.append("")

    return "\n".join(parts).strip()


# ------------------------------------------------------------
# Pattern rendering (human DSL)
# ------------------------------------------------------------


def _render_pattern_readable(p: PatternNode) -> str:
    return " ".join(
        item.expression for item in p.items if not isinstance(item, SpacerNode)
    )


# ------------------------------------------------------------
# Action rendering (human DSL)
# ------------------------------------------------------------


def _render_action_readable(actions):
    if not actions:
        return ""

    a = actions[0]

    if a.eof_action:
        return "EOF"

    if a.error_pattern:
        return f"Error({a.error_pattern})"

    if a.line_action and a.record_action:
        if a.state:
            return f"{a.line_action}.{a.record_action}({a.state})"
        return f"{a.line_action}.{a.record_action}"

    if a.line_action:
        if a.state:
            return f"{a.line_action}({a.state})"
        return a.line_action

    if a.record_action:
        if a.state:
            return f"{a.record_action}({a.state})"
        return a.record_action

    if a.state:
        return f"{a.state}"

    raise ValueError(f"Cannot render action: {a}")
