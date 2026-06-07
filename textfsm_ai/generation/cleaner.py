"""
TextFSM structural detection, correction, and self-healing pipeline.

Pipeline:
  dedent -> validate -> drift-clean -> validate -> fallback/full-clean
"""

from __future__ import annotations

import re
import textwrap
from io import StringIO

import textfsm

# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------


def validate_template(template: str) -> bool:
    try:
        textfsm.TextFSM(StringIO(template))
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def clean_template(template: str) -> str:
    # Step 1: dedent + strip + remove comments
    normalized = cleanup_comment(textwrap.dedent(template).strip())

    # Fast path: dedented template is valid
    if validate_template(normalized):
        drift_cleaned = cleanup_invalidate_state_transition(normalized)
        return drift_cleaned if validate_template(drift_cleaned) else normalized

    # Slow path: dedented template is invalid → full cleanup
    cleaned = full_cleanup(normalized)

    return cleaned if validate_template(cleaned) else template


# ---------------------------------------------------------------------------
# Full cleanup (slow path)
# ---------------------------------------------------------------------------


def full_cleanup(template: str) -> str:
    template = cleanup_invalidate_state_transition(template)
    template = correct_start_state(template)

    parts = []
    for line in template.splitlines():
        stripped = line.strip()

        # Blank line
        if not stripped:
            parts.append("")
            continue

        # Value line
        if is_value_line(line):
            parts.append(clean_value_line(line))
            continue

        # State header
        if is_state_header(line):
            parts.append(clean_state_header(line, parts))
            continue

        # Rule line
        if is_rule_line(line):
            parts.append(clean_rule_line(line))
            continue

        # Fallback
        parts.append(stripped)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Value line helpers
# ---------------------------------------------------------------------------


def is_value_line(line: str) -> bool:
    return bool(re.match(r"(?i)^value\s+", line))


def clean_value_line(line: str) -> str:
    pat = r"(?i)^Value(\s+[a-z,]+)?\s+(\S+)\s+(\(.+)"
    m = re.match(pat, line.strip())
    if not m:
        return line.strip()

    options, name, pattern = m.groups()
    name = name.lower()

    if options:
        options = re.sub(r"\s*,\s*", ",", options.strip()).title()
        return f"Value {options} {name} {pattern}"

    return f"Value {name} {pattern}"


# ---------------------------------------------------------------------------
# State header helpers
# ---------------------------------------------------------------------------


def is_state_header(line: str) -> bool:
    return bool(re.match(r"^\w+$", line.strip()))


def clean_state_header(line: str, parts: list[str]) -> str:
    name = line.strip()

    if name.lower() == "start":
        if parts and parts[-1] != "":
            parts.append("")
        return "Start"

    if parts and parts[-1] != "":
        parts.append("")

    return name


# ---------------------------------------------------------------------------
# Rule line helpers
# ---------------------------------------------------------------------------


def is_rule_line(line: str) -> bool:
    return bool(re.match(r"^\s*\^", line))


def clean_rule_line(line: str) -> str:
    stripped = line.strip()

    # No action → indent only
    if "->" not in stripped:
        return "  " + stripped

    rules, action = stripped.rsplit("->", 1)
    action = normalize_action_expression(action.strip())
    return f"  {rules.strip()} -> {action}"


# ---------------------------------------------------------------------------
# Start state correction
# ---------------------------------------------------------------------------


def correct_start_state(template: str) -> str:
    # If Start already exists, keep as-is
    if re.search(r"(?im)^\s*Start\s*$", template):
        return template

    lines = template.splitlines()
    parts = []
    inserted = False

    for index, line in enumerate(lines):
        parts.append(line)

        # Insert Start after last Value block
        if not inserted and re.match(r"(?i)^value\s+", line):
            if index + 1 < len(lines):
                next_line = lines[index + 1]
                if not re.match(r"(?i)^\s*value\s+", next_line):
                    parts.append("")
                    parts.append("Start")
                    inserted = True

    if not inserted:
        # No Value lines found; prepend Start
        return "Start\n" + "\n".join(lines)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Comment cleanup
# ---------------------------------------------------------------------------


def cleanup_comment(template: str) -> str:
    return "\n".join(
        line for line in template.splitlines() if not line.strip().startswith("#")
    )


# ---------------------------------------------------------------------------
# Drift cleanup
# ---------------------------------------------------------------------------


def cleanup_invalidate_state_transition(template: str) -> str:
    lines = template.splitlines()
    parts = []

    for index, line in enumerate(lines):
        stripped = line.strip()

        # Always keep Value, Start, rule lines, blanks
        if re.match(r"^Value\b|^Start\b|^\s*\^", line) or not stripped:
            parts.append(line)
            continue

        # Candidate state-transition or stray word
        if re.match(r"^\w", line):
            tokens = re.findall(r"\S+", line)
            if len(tokens) > 1:
                continue

            state_transition = stripped

            # If it looks like an action keyword, drop it
            if re.search(
                r"(?i)\b(record|norecord|clear|clearall|next|continue)\b",
                state_transition,
            ):
                continue

            # Keep only if referenced in some "-> ..." action above
            has_transition = False
            for prev in lines[:index]:
                if "->" not in prev:
                    continue
                _, action = prev.rsplit("->", maxsplit=1)
                if state_transition in action:
                    has_transition = True
                    break

            if has_transition:
                parts.append(line)

            continue

        # Fallback
        parts.append(line)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Action normalization
# ---------------------------------------------------------------------------

ACTION_MAP = {
    "next": "Next",
    "continue": "Continue",
    "record": "Record",
    "norecord": "NoRecord",
    "clear": "Clear",
    "clearall": "Clearall",
}


def normalize_action_token(token: str) -> str:
    key = token.lower()
    return ACTION_MAP.get(key, token)


def normalize_action_expression(expr: str) -> str:
    parts = re.split(r"(\W+)", expr)
    normalized = []

    for part in parts:
        if not part:
            continue

        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", part):
            normalized.append(normalize_action_token(part))
        else:
            normalized.append(part)

    return "".join(normalized)
