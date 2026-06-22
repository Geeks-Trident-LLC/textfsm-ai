# textfsm_ai/generation/engine/validator.py

import re
from io import StringIO
from typing import Dict, List, Tuple

import textfsm

from textfsm_ai.generation.core.models import (
    TemplateFindingResult,
    TemplateValidationResult,
)

# -------------------------------
# Template validation
# -------------------------------


def validate_template(template: str) -> TemplateValidationResult:
    if not isinstance(template, str) or not template.strip():
        return TemplateValidationResult(
            template=template,
            reason=(
                "Template must be a non-empty string, "
                f"but received {type(template)} with {len(template.strip())} chars"
            ),
            ready=False,
        )

    try:
        textfsm.TextFSM(StringIO(template))
        return TemplateValidationResult(template=template, ready=True)
    except Exception as ex:
        return TemplateValidationResult(
            template=template,
            reason=f"{type(ex).__name__}: {ex}",
            ready=False,
        )


# ---------------------------------------------------------
# 1. Syntax + parsing
# ---------------------------------------------------------
class TemplateRecordValidator:
    """Modular validator for comparing parsed TextFSM records."""

    def __init__(self, expected: List[Dict[str, str]]):
        # Normalize expected keys to lowercase
        self.expected = [{k.lower(): v for k, v in row.items()} for row in expected]
        self.expected_keys = set(self.expected[0].keys()) if self.expected else set()

    def compare_row_count(self, parsed: List[Dict[str, str]]) -> List[str]:
        findings = []
        if len(parsed) != len(self.expected):
            findings.append(
                f"row_count_mismatch: parsed={len(parsed)}, "
                f"expected={len(self.expected)}"
            )
        return findings

    def check_variable_case(self, row: Dict[str, str]) -> List[str]:
        findings: List[str] = []
        for k in row.keys():
            if k != k.lower():
                findings.append(f"invalid_variable_case: '{k}' must be lowercase")
        return findings

    def compare_keys(self, parsed_norm: Dict[str, str]) -> List[str]:
        findings = []
        for k in parsed_norm.keys():
            if k not in self.expected_keys:
                findings.append(f"unexpected_key: '{k}' not in expected keys")

        for k in self.expected_keys:
            if k not in parsed_norm:
                findings.append(f"missing_key: '{k}' missing in parsed row")
        return findings

    def compare_values(
        self, parsed_norm: Dict[str, str], expected_row: Dict[str, str]
    ) -> List[str]:
        findings = []
        for k in self.expected_keys:
            if parsed_norm.get(k) != expected_row.get(k):
                findings.append(
                    f"value_mismatch: key='{k}', parsed='{parsed_norm.get(k)}', "
                    f"expected='{expected_row.get(k)}'"
                )
        return findings

    def compare(self, parsed: List[Dict[str, str]]) -> Tuple[List[str], bool]:
        findings = []

        # Row count mismatch
        findings.extend(self.compare_row_count(parsed))
        if findings:
            return findings, False

        # Row-by-row comparison
        for idx, row in enumerate(parsed):
            parsed_norm = {k.lower(): v for k, v in row.items()}
            expected_row = self.expected[idx]

            findings.extend(self.check_variable_case(row))
            findings.extend(self.compare_keys(parsed_norm))
            findings.extend(self.compare_values(parsed_norm, expected_row))

        return findings, len(findings) == 0


def validate_template_and_records(
    template: str, sample: str, expected_records: List[Dict[str, str]]
):
    """
    Returns:
      findings: list[str]
      ready: bool
    """
    findings: list[str] = []

    # 1. Compile template
    try:
        fsm = textfsm.TextFSM(StringIO(template))
    except Exception as ex:
        return [f"template_syntax_error: {type(ex).__name__}: {ex}"], False

    # 2. Parse sample
    try:
        parsed = fsm.ParseTextToDicts(sample)
    except Exception as ex:
        return [f"template_parse_error: {type(ex).__name__}: {ex}"], False

    # 3. Compare parsed vs expected
    validator = TemplateRecordValidator(expected_records)
    findings, ok = validator.compare(parsed)

    return findings, ok


# ---------------------------------------------------------
# 2. Extract normalized lines
# ---------------------------------------------------------
def extract_lines(template: str):
    return [
        line.rstrip()
        for line in template.strip().splitlines()
        if not re.match(r"\s*#", line)
    ]


# ---------------------------------------------------------
# 3. Value definitions
# ---------------------------------------------------------
def check_value_definitions(lines: list[str]):
    findings: list[str] = []
    values = []

    for line in lines:
        if not line.strip():
            continue
        if not re.match(r"value ", line, re.IGNORECASE):
            break
        values.append(line)

    pat1 = r"Value\s+(\w+)\s+\((.*)\)\s*$"
    pat2 = r"Value\s+([A-Za-z]+(?:,[A-Za-z]+)*)\s+(\w+)\s+\((.*)\)\s*$"

    allowed_opts = {"Fillup", "Filldown", "Required", "Key", "List"}

    for vline in values:
        m1 = re.fullmatch(pat1, vline)
        m2 = re.fullmatch(pat2, vline)

        if not m1 and not m2:
            findings.append(f"invalid_value_definition: {vline}")
            continue

        if m1:
            var = m1.group(1)
            regex = m1.group(2)

            if var in allowed_opts:
                findings.append(f"invalid_variable_name: {var} in {vline}")

            if not regex.strip():
                findings.append(f"empty_regex: {vline}")

            try:
                re.compile(regex)
            except Exception as ex:
                findings.append(f"regex_compile_error: {ex} in {vline}")

            continue

        opts = m2.group(1).split(",") if m2 else ""
        var = m2.group(2) if m2 else ""
        regex = m2.group(3) if m2 else ""

        if any(o not in allowed_opts for o in opts):
            findings.append(f"invalid_value_options: {opts} in {vline}")

        if var in allowed_opts:
            findings.append(f"invalid_variable_name: {var} in {vline}")

        if not regex.strip():
            findings.append(f"empty_regex: {vline}")

        try:
            re.compile(regex)
        except Exception as ex:
            findings.append(f"regex_compile_error: {ex} in {vline}")

    return findings


# ---------------------------------------------------------
# 4. Start state
# ---------------------------------------------------------
def check_start_state(lines: list[str]):
    findings = []
    found = False

    for idx, line in enumerate(lines):
        if re.fullmatch("start", line, re.IGNORECASE):
            if line != "Start":
                findings.append(f"start_state_casing_error: {line}")
                continue

            if found:
                findings.append("multiple_start_state")
                continue

            found = True

            if idx > 0 and lines[idx - 1].strip():
                findings.append("start_state_preceding_newline_error")

    if not found:
        findings.append("missing_start_state")

    return findings


# ---------------------------------------------------------
# 5. Transition states
# ---------------------------------------------------------
def check_transition_states(lines: list[str]):
    findings = []
    forbidden = {
        "Next",
        "Continue",
        "Record",
        "NoRecord",
        "Clear",
        "Clearall",
        "EOF",
        "Error",
    }

    for line in lines:
        if line in forbidden:
            findings.append(f"forbidden_state_name: {line}")
            continue

        if not re.fullmatch(r"[A-Za-z]\w*", line):
            continue  # not a state header

    return findings


# ---------------------------------------------------------
# 6. Rule actions
# ---------------------------------------------------------
def check_rule_actions(lines: list[str]):
    findings = []
    allowed = {"Next", "Continue", "Record", "NoRecord", "Clear", "Clearall"}

    pat = r"(\s{2,})(.+?)(?:\s+->\s+(.*))?$"

    for line in lines:
        m = re.fullmatch(pat, line)
        if not m:
            continue

        rule = m.group(2)
        action = m.group(3)

        if not rule.startswith("^"):
            findings.append(f"invalid_rule_definition: {line}")

        if not action:
            continue

        token = action.split()[0]

        if token not in allowed and token != "Error":
            findings.append(f"invalid_action: {token} in {line}")

    return findings


def check_rule_spacers(lines: list[str]):
    findings = []
    pat = r"(\s{2,})(.+?)(?:\s+->\s+(.*))?$"
    spacers = []

    for line in lines:
        m = re.fullmatch(pat, line)
        if not m:
            continue
        spacers.append(m.group(1))

    if spacers and len(set(spacers)) != 1:
        findings.append(
            "inconsistent_rule_definition_spacers: "
            f'expected consistent "  ", but received {spacers}'
        )

    return findings


# ---------------------------------------------------------
# 7. Main entry point
# ---------------------------------------------------------
def find_template_issues(
    template: str, records: list, sample: str
) -> TemplateFindingResult:
    findings = []

    syntax_findings, ready = validate_template_and_records(template, sample, records)
    if ready:
        return TemplateFindingResult(template, records, sample, [], ready=True)

    findings.extend(syntax_findings)

    lines = extract_lines(template)

    findings.extend(check_value_definitions(lines))
    findings.extend(check_start_state(lines))
    findings.extend(check_transition_states(lines))
    findings.extend(check_rule_actions(lines))
    findings.extend(check_rule_spacers(lines))

    return TemplateFindingResult(
        template=template,
        records=records,
        sample=sample,
        findings=findings,
        reason="; ".join(findings),
        ready=False,
    )
