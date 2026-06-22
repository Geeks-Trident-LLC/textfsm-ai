import re
from typing import Any, Dict, List, Optional, Tuple

from textfsm_ai.dsl.core.models import DSLExtractorResult
from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.core.patterns import KEYWORD_TO_BASE

STATE_HEADER_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*$")
RULE_LINE_RE = re.compile(r"^\s+(.*\S.*)$")

# Supports:
#   keyword()
#   keyword(var-name)
#   keyword(var-name, options-List)
#   keyword(var-name, options-Required,List)
KEYWORD_CALL_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9-]+)"
    r"\("
    r"(?:"  # optional args
    r"var-(?P<var>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*,\s*(?P<options>[A-Za-z0-9-,]+))?"
    r")?"
    r"\)$"
)


def parse_human_dsl(human_dsl: str) -> List[Tuple[str, List[str]]]:
    """Collect states and their rules from human DSL, preserving order."""
    lines = human_dsl.splitlines()
    collected: List[Tuple[str, List[str]]] = []
    current_state = None
    current_rules: List[str] = []

    for line in lines:
        m_state = STATE_HEADER_RE.match(line)
        if m_state:
            if current_state is not None:
                collected.append((current_state, current_rules))
            current_state = m_state.group(1)
            current_rules = []
            continue

        m_rule = RULE_LINE_RE.match(line)
        if m_rule and current_state is not None:
            current_rules.append(m_rule.group(1))
            continue

    if current_state is not None:
        collected.append((current_state, current_rules))

    return collected


def split_body_and_action(rule: str) -> Tuple[str, Optional[str]]:
    """Split a rule into body and optional action."""
    if "->" not in rule:
        return rule, None
    body, action = rule.split("->", 1)
    return body.rstrip(), action.strip() or None


def strip_prefix_suffix(body: str) -> str:
    """Replace start() → ^ and end() → $$."""
    body = body.strip()

    if not body.startswith("start()"):
        raise ValueError(f"Rule must start with start(): {body}")

    body = body[len("start()") :].lstrip()

    if body.endswith(" end()"):
        body = body[: -len(" end()")].rstrip() + "$$"

    return "^" + body


def tokenize_human_dsl_body(body: str) -> List[str]:
    """Tokenize human-DSL body, keeping KeywordCalls as single tokens."""
    tokens: List[str] = []
    i = 0
    n = len(body)

    while i < n:
        ch = body[i]

        # whitespace
        if ch.isspace():
            j = i
            while j < n and body[j].isspace():
                j += 1
            tokens.append(body[i:j])
            i = j
            continue

        # potential keyword (alnum or '-')
        if ch.isalnum() or ch == "-":
            j = i
            while j < n and (body[j].isalnum() or body[j] == "-"):
                j += 1

            # keyword call: keyword(...)
            if j < n and body[j] == "(":
                depth = 1
                j += 1
                while j < n and depth > 0:
                    if body[j] == "(":
                        depth += 1
                    elif body[j] == ")":
                        depth -= 1
                    j += 1
                tokens.append(body[i:j])
                i = j
                continue

        # literal token: read until whitespace
        j = i
        while j < n and not body[j].isspace():
            j += 1
        tokens.append(body[i:j])
        i = j

    return tokens


def parse_keyword_call(token: str):
    """Return (keyword, varname, options_string) or None."""
    m = KEYWORD_CALL_RE.match(token)
    if not m:
        return None

    keyword = m.group("name")
    varname = m.group("var")
    options_raw = m.group("options")

    if options_raw:
        # strip leading "options-" if present
        if options_raw.startswith("options-"):
            options = options_raw[len("options-") :]
        else:
            options = options_raw
    else:
        options = ""

    return keyword, varname, options


def ensure_variable(
    variables: List[Dict[str, Any]],
    var_lookup: Dict[str, Dict[str, Any]],
    keyword: str,
    varname: str,
    expression: str,
    options: str,
):
    """Create variable entry if not already present."""
    if varname in var_lookup:
        return

    base = KEYWORD_TO_BASE[keyword]
    node = create_node(keyword, varname=varname)

    var_def = {
        "name": varname,
        "keyword": keyword,
        "category": base.name,
        "options": options,  # e.g. "Required,List"
        "expression": expression,
        "expression_regex": node.to_expression_regex(),
    }

    variables.append(var_def)
    var_lookup[varname] = var_def


def tokens_to_pattern(
    body: str,
    variables: List[Dict[str, Any]],
    var_lookup: Dict[str, Dict[str, Any]],
) -> str:
    """Convert tokenized body into a regex pattern."""
    tokens = tokenize_human_dsl_body(body)
    parts: List[str] = []

    for tok in tokens:
        if tok.isspace():
            parts.append(r"\s+")
            continue

        kc = parse_keyword_call(tok)
        if kc:
            keyword, varname, options = kc

            if varname:
                expr = f"{keyword}(var-{varname}"
                if options:
                    expr += f", options-{options}"
                expr += ")"
                ensure_variable(variables, var_lookup, keyword, varname, expr, options)
                parts.append(f"${{{varname}}}")
            else:
                node = create_node(keyword)
                parts.append(node.to_expression_regex())
            continue

        parts.append(re.escape(tok))

    return "".join(parts)


def human_dsl_to_machine_dsl(human_dsl: str) -> DSLExtractorResult:
    """Convert human-readable DSL back into machine DSL."""
    collected = parse_human_dsl(human_dsl)

    variables: List[Dict[str, Any]] = []
    var_lookup: Dict[str, Dict[str, Any]] = {}
    states: List[Dict[str, Any]] = []

    for state_name, rules in collected:
        transitions: List[Dict[str, Any]] = []

        for rule in rules:
            body, action = split_body_and_action(rule)
            body = strip_prefix_suffix(body)

            has_end = body.endswith("$$")
            if has_end:
                body_core = body[1:-2]
            else:
                body_core = body[1:]

            pattern_core = tokens_to_pattern(body_core, variables, var_lookup)
            pattern = "^" + pattern_core
            if has_end:
                pattern += "$$"

            transitions.append(
                {
                    "pattern": pattern,
                    "action": action,
                }
            )

        states.append(
            {
                "name": state_name,
                "transitions": transitions,
            }
        )

    return DSLExtractorResult(states=states, variables=variables, ready=True)
