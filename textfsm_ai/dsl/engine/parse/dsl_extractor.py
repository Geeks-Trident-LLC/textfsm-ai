# textfsm_ai/dsl/engine/parse/dsl_extractor.py

import re
from typing import Any, Dict, List, Optional

from textfsm_ai.dsl.core.models import DSLExtractorResult
from textfsm_ai.dsl.core.nodes import create_node
from textfsm_ai.dsl.core.patterns import KEYWORD_TO_BASE, PATTERNS

VALUE_RE = re.compile(
    r"^Value"
    r"(?:\s+((?:Required|List|Key|Filldown|Fillup)"
    r"(?:,(?:Required|List|Key|Filldown|Fillup))*))?"
    r"\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"\s*\((.+)\)\s*$"
)

STATE_RE = re.compile(r"^(\w+)\s*$")
TRANSITION_RE = re.compile(r"^\s*(\^.+?)\s*(?:->\s*(.+))?$")


class DSLExtractor:
    """Extract machine-DSL structure from a canonical TextFSM template."""

    def __init__(self, template: str):
        self.template = template
        self.lines = template.splitlines()
        self.variables: List[Dict[str, Any]] = []
        self.states: List[Dict[str, Any]] = []
        self.current_state: Optional[Dict[str, Any]] = None

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def extract(self) -> DSLExtractorResult:
        for line in self.lines:
            try:
                if self._parse_value(line):
                    continue
            except Exception as ex:
                return self._fail(f"{type(ex).__name__}: {ex}")

            if self._parse_state(line):
                continue
            if self._parse_transition(line):
                continue

        return DSLExtractorResult(
            template=self.template,
            variables=self.variables,
            states=self.states,
            ready=True,
        )

    # ---------------------------------------------------------
    # Parsing helpers
    # ---------------------------------------------------------
    def _parse_value(self, line: str) -> bool:
        m = VALUE_RE.match(line)
        if not m:
            return False

        options, varname, regex = m.groups()

        keyword = self._lookup_keyword(regex)
        if keyword is None:
            raise RuntimeError(f"Unknown regex pattern: {regex!r}")

        node = create_node(keyword, varname, extra=options or "", generalize=True)

        self.variables.append(
            {
                "name": varname,
                "keyword": keyword,
                "category": KEYWORD_TO_BASE[keyword].name,
                "options": options or "",
                "expression": node.to_expression(),
                "expression_regex": node.to_expression_regex(),
            }
        )
        return True

    def _parse_state(self, line: str) -> bool:
        m = STATE_RE.match(line)
        if not m:
            return False

        name = m.group(1)
        self.current_state = {"name": name, "transitions": []}
        self.states.append(self.current_state)
        return True

    def _parse_transition(self, line: str) -> bool:
        if not self.current_state:
            return False

        m = TRANSITION_RE.match(line)
        if not m:
            return False

        pattern, action = m.groups()
        self.current_state["transitions"].append(
            {
                "pattern": pattern,
                "action": action or None,
            }
        )
        return True

    # ---------------------------------------------------------
    # Utility helpers
    # ---------------------------------------------------------
    def _lookup_keyword(self, regex: str) -> Optional[str]:
        for k, p in PATTERNS.items():
            if p.regex == regex:
                return k
        return None

    def _fail(self, reason: str) -> DSLExtractorResult:
        return DSLExtractorResult(
            template=self.template,
            reason=reason,
            ready=False,
        )


# ---------------------------------------------------------
# Public function
# ---------------------------------------------------------
def extract_machine_dsl(canonical_template: str) -> DSLExtractorResult:
    return DSLExtractor(canonical_template).extract()
