# textfsm_ai/dsl/ast/parser.py

import re
from typing import Dict, List, Optional

from textfsm_ai.dsl.ast.nodes import (
    Action,
    CallNode,
    EndNode,
    LiteralNode,
    PatternItem,
    PatternNode,
    RuleNode,
    SpacerNode,
    StartNode,
    StateNode,
    TemplateAST,
    ValueNode,
    VarNode,
)
from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.core.patterns import PATTERNS
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword

VALUE_RE = re.compile(
    r"^Value"
    r"(?:\s+([A-Za-z0-9_,]+))?"  # options
    r"\s+([A-Za-z_][A-Za-z0-9_]*)"  # varname
    r"\s*\((.+)\)\s*$"  # regex
)

STATE_RE = re.compile(r"^(\w+)\s*$")
RULE_RE = re.compile(r"^\s*(\^.+?)\s*(?:->\s*(.+?)\s*)?$")

VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)\(\)")


# ------------------------------------------------------------
# Action parsing
# ------------------------------------------------------------


def parse_action_expr(expr: str) -> Action:
    expr = expr.strip()

    # ------------------------------------------------------------
    # EOF
    # ------------------------------------------------------------
    if expr == "EOF":
        return Action(eof_action=True)

    # ------------------------------------------------------------
    # Error ^pattern$
    # ------------------------------------------------------------
    if expr.startswith("Error "):
        pattern = expr[len("Error ") :].strip()
        return Action(error_pattern=pattern)

    # ------------------------------------------------------------
    # Combined: Next.Record Foo
    # ------------------------------------------------------------
    if "." in expr:
        line_part, rest = expr.split(".", 1)
        parts = rest.strip().split()
        record_part = parts[0]
        state = parts[1] if len(parts) > 1 else None
        return Action(
            line_action=line_part,
            record_action=record_part,
            state=state,
        )

    # ------------------------------------------------------------
    # Split into head + tail
    # ------------------------------------------------------------
    parts = expr.split()
    head = parts[0]
    tail = parts[1:] if len(parts) > 1 else []

    # ------------------------------------------------------------
    # Line-only: Next Foo, Continue Bar
    # ------------------------------------------------------------
    if head in ("Next", "Continue"):
        return Action(
            line_action=head,
            state=tail[0] if tail else None,
        )

    # ------------------------------------------------------------
    # Record-only: Record Foo, NoRecord Bar, Clear Baz, Clearall Qux
    # ------------------------------------------------------------
    if head in ("Record", "NoRecord", "Clear", "Clearall"):
        return Action(
            record_action=head,
            state=tail[0] if tail else None,
        )

    # ------------------------------------------------------------
    # ⭐ NEW: State-only transition
    # e.g. "Start"
    # ------------------------------------------------------------
    if len(parts) == 1:
        return Action(
            line_action=None,
            record_action=None,
            state=head,
        )

    # ------------------------------------------------------------
    # Otherwise invalid
    # ------------------------------------------------------------
    raise ValueError(f"Unknown action expression: {expr}")


# ------------------------------------------------------------
# Pattern parsing (simplified DSL grammar)
# ------------------------------------------------------------


def _lookup_value(values_by_name: Dict[str, ValueNode], name: str) -> ValueNode:
    try:
        return values_by_name[name]
    except KeyError:
        raise KeyError(f"Unknown variable: {name!r}")


def parse_pattern(pattern: str, values_by_name: Dict[str, ValueNode]) -> PatternNode:
    nodes: List[PatternItem] = []

    # ------------------------------------------------------------
    # 1. Extract prefix "^"
    # ------------------------------------------------------------
    prefix = pattern.startswith("^")
    if prefix:
        nodes.append(
            StartNode(
                raw="^",
                textfsm_repr="^",
                expression="start()",
                regex="^",
            )
        )
        pattern = pattern[1:]  # remove prefix

    # ------------------------------------------------------------
    # 2. Extract suffix "$$"
    # ------------------------------------------------------------
    suffix = pattern.endswith("$$")
    if suffix:
        body = pattern[:-2]
    else:
        body = pattern

    # ------------------------------------------------------------
    # 3. Parse body
    # ------------------------------------------------------------
    nodes.extend(parse_body_pattern(body, values_by_name))

    # ------------------------------------------------------------
    # 4. Add suffix node
    # ------------------------------------------------------------
    if suffix:
        nodes.append(
            EndNode(
                raw="$$",
                textfsm_repr="$$",
                expression="end()",
                regex="$",
            )
        )

    return PatternNode(items=nodes)


VAR_GROUP_RE = re.compile(
    r"\(\$\{([A-Za-z_][A-Za-z0-9_]*)\}\)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}"
)


def parse_body_pattern(
    body: str, values_by_name: Dict[str, ValueNode]
) -> List[PatternItem]:
    nodes = []
    pos = 0
    for m in VAR_GROUP_RE.finditer(body):
        start, end = m.span()

        # literal text before match
        if start > pos:
            literal = body[pos:start]
            nodes.extend(parse_literal_text(literal))

        # var name (group 1 or group 2)
        varname = m.group(1) or m.group(2)
        v = values_by_name[varname]

        # append VarNode (inferred)
        if v.infer:
            nodes.append(v.infer)

        pos = end

    # trailing literal text
    if pos < len(body):
        nodes.extend(parse_literal_text(body[pos:]))

    return nodes


WS_RE = re.compile(r"\s+|\\s(?:[+*])?")
PUNCTS_RE = re.compile(PATTERNS["puncts-group"].regex)


def parse_literal_text(text: str) -> List[PatternItem]:
    nodes = []
    pos = 0

    for m in PUNCTS_RE.finditer(text):
        start, end = m.span()

        # pre-match literal
        if start > pos:
            segment = text[pos:start]
            nodes.extend(_parse_literal_segment(segment))

        # puncts-group match
        raw = m.group(0)
        nodes.append(
            CallNode(
                raw=raw,
                textfsm_repr=raw,
                expression="puncts-group()",
                regex=PATTERNS["puncts-group"].regex,
            )
        )

        pos = end

    # trailing literal
    if pos < len(text):
        nodes.extend(_parse_literal_segment(text[pos:]))

    return nodes


def _parse_literal_segment(segment: str) -> List[PatternItem]:
    nodes = []
    pos = 0

    for m in WS_RE.finditer(segment):
        start, end = m.span()

        # pre-whitespace literal
        if start > pos:
            raw = segment[pos:start]
            nodes.append(_literal_or_digit(raw))

        # whitespace
        ws = m.group(0)
        nodes.append(
            SpacerNode(
                raw=ws,
                textfsm_repr="\\s+",
                expression=" ",
                regex="\\s+",
            )
        )

        pos = end

    # trailing literal
    if pos < len(segment):
        raw = segment[pos:]
        nodes.append(_literal_or_digit(raw))

    return nodes


def _literal_or_digit(raw: str) -> PatternItem:
    if any(ch.isdigit() for ch in raw):
        # infer keyword
        keyword = infer_base_keyword([raw])
        node = create_node(keyword, generalize=True)
        return CallNode(
            raw=raw,
            textfsm_repr=raw,
            expression=node.to_expression(),
            regex=node.to_regex(),
        )

    # plain literal
    return LiteralNode(
        raw=raw,
        textfsm_repr=raw,
        expression=raw,
        regex=raw,
    )


# ------------------------------------------------------------
# Rule + template parsing
# ------------------------------------------------------------


def parse_rule_line(
    line: str, values_by_name: Dict[str, ValueNode]
) -> Optional[RuleNode]:

    m = RULE_RE.match(line)
    if not m:
        return None

    if " -> " in line:
        pattern_text, action_expr = m.groups()
        pattern = parse_pattern(pattern_text.lstrip(), values_by_name)
        action = parse_action_expr(action_expr)

        return RuleNode(pattern=pattern, actions=[action])

    pattern = parse_pattern(line.lstrip(), values_by_name)
    return RuleNode(pattern=pattern, actions=[])


def parse_textfsm(template: str, records: List[dict]) -> TemplateAST:
    ast = TemplateAST()
    current_state_name: Optional[str] = None
    current_state_lines: List[str] = []

    def flush_state():
        nonlocal current_state_name, current_state_lines
        if current_state_name is not None:
            state = StateNode(name=current_state_name)
            values_by_name = {v.name: v for v in ast.values}
            for line in current_state_lines:
                rule = parse_rule_line(line, values_by_name)
                if rule:
                    state.rules.append(rule)
            ast.states.append(state)
        current_state_name = None
        current_state_lines = []

    # 1) parse values + states/rules (structure only)
    for raw_line in template.splitlines():
        line = raw_line.rstrip()

        if not line or line.lstrip().startswith("#"):
            continue

        m = VALUE_RE.match(line)
        if m:
            options, varname, regex = m.groups()
            opts = options.split(",") if options else None
            values = [record[varname] for record in records]
            keyword = infer_base_keyword(values)

            node = create_node(
                keyword, varname=varname, extra=options or "", generalize=True
            )
            var_node = VarNode(
                raw=f"${{{varname}}}",
                textfsm_repr=f"${{{varname}}}",
                expression=node.to_expression(),
                regex=node.to_regex(),
            )

            ast.values.append(
                ValueNode(
                    name=varname,
                    regex=regex,
                    options=opts,
                    infer=var_node,
                )
            )
            continue

        if STATE_RE.match(line) and not line.startswith(" "):
            flush_state()
            current_state_name = line.strip()
            continue

        if current_state_name is not None:
            current_state_lines.append(line)

    flush_state()

    return ast
