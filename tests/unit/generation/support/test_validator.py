# tests/unit/generation/support/test_validator.py

from textfsm_ai.generation.core.models import (
    TemplateFindingResult,
    TemplateValidationResult,
)
from textfsm_ai.generation.support.validator import (
    check_rule_actions,
    check_rule_spacers,
    check_start_state,
    check_transition_states,
    check_value_definitions,
    extract_lines,
    find_template_issues,
    validate_template,
    validate_template_and_records,
)


# ---------------------------------------------------------
# validate_template
# ---------------------------------------------------------
def test_validate_template_success():
    template = """
Value name (\\S+)

Start
  ^Name: ${name} -> Record
""".strip()
    result = validate_template(template)
    assert isinstance(result, TemplateValidationResult)
    assert result.ready is True
    assert result.reason == ""


def test_validate_template_empty():
    result = validate_template("")
    assert result.ready is False
    assert "non-empty string" in result.reason


def test_validate_template_invalid_syntax():
    template = "Value name (\\S+)\nStart\n  ^ -> Record"
    result = validate_template(template)
    assert result.ready is False
    assert "FSMTemplateError" in result.reason or "Error" in result.reason


# ---------------------------------------------------------
# validate_template_and_records
# ---------------------------------------------------------
def test_validate_template_and_records_success():
    template = """
Value iface (\\S+)

Start
  ^interface ${iface} -> Record
""".strip()
    sample = "interface Gi0/1"
    expected = [{"iface": "Gi0/1"}]

    findings, ready = validate_template_and_records(template, sample, expected)
    assert findings == []
    assert ready is True


def test_validate_template_and_records_mismatch():
    template = """
Value iface (\\S+)

Start
  ^interface ${iface} -> Record
""".strip()
    sample = "interface Gi0/1"
    expected = [{"iface": "Gi0/2"}]  # mismatch

    findings, ready = validate_template_and_records(template, sample, expected)
    assert ready is False
    assert "value_mismatch" in findings[0]


def test_validate_template_and_records_syntax_error():
    template = "Value iface (\\S+)\nStart\n  ^ -> Record"
    findings, ready = validate_template_and_records(template, "x", [])
    assert ready is False
    assert "template_syntax_error" in findings[0]


def test_validate_template_and_records_parse_error():
    template = """
Value iface (\\S+)

Start
  ^interface ${iface} -> Continue
  ^bad -> Error "boom"
""".strip()
    sample = "interface Gi0/1\nbad\n"

    findings, ready = validate_template_and_records(template, sample, [])
    assert ready is False
    assert any("template_parse_error" in f for f in findings)


# ---------------------------------------------------------
# extract_lines
# ---------------------------------------------------------
def test_extract_lines_removes_comments_and_strips():
    template = """
# comment
Value name (\\S+)
Start
  ^foo -> Record
""".strip()
    lines = extract_lines(template)
    assert lines == ["Value name (\\S+)", "Start", "  ^foo -> Record"]


# ---------------------------------------------------------
# check_value_definitions
# ---------------------------------------------------------
def test_check_value_definitions_valid():
    lines = [
        "Value iface (\\S+)",
        "Value Required,Filldown name (\\S+)",
        "Start",
    ]
    findings = check_value_definitions(lines)
    assert findings == []


def test_check_value_definitions_invalid_format():
    lines = ["Value iface \\S+", "Start"]
    findings = check_value_definitions(lines)
    assert any("invalid_value_definition" in f for f in findings)


def test_check_value_definitions_invalid_regex():
    lines = ["Value iface (++)", "Start"]
    findings = check_value_definitions(lines)
    assert any("regex_compile_error" in f for f in findings)


def test_check_value_definitions_pat1_invalid_variable_name():
    # No options prefix, so "Required" is parsed as the variable name itself.
    lines = ["Value Required (\\S+)", "Start"]
    findings = check_value_definitions(lines)
    assert any("invalid_variable_name" in f for f in findings)


def test_check_value_definitions_pat1_empty_regex():
    lines = ["Value iface ()", "Start"]
    findings = check_value_definitions(lines)
    assert any("empty_regex" in f for f in findings)


def test_check_value_definitions_pat2_invalid_option():
    lines = ["Value BadOpt iface (\\S+)", "Start"]
    findings = check_value_definitions(lines)
    assert any("invalid_value_options" in f for f in findings)


def test_check_value_definitions_pat2_invalid_variable_name():
    lines = ["Value Required Key (\\S+)", "Start"]
    findings = check_value_definitions(lines)
    assert any("invalid_variable_name" in f for f in findings)


def test_check_value_definitions_pat2_empty_regex():
    lines = ["Value Required iface ()", "Start"]
    findings = check_value_definitions(lines)
    assert any("empty_regex" in f for f in findings)


def test_check_value_definitions_pat2_regex_compile_error():
    lines = ["Value Required iface (abc[def)", "Start"]
    findings = check_value_definitions(lines)
    assert any("regex_compile_error" in f for f in findings)


# ---------------------------------------------------------
# check_start_state
# ---------------------------------------------------------
def test_check_start_state_valid():
    lines = ["Value iface (\\S+)", "", "Start"]
    findings = check_start_state(lines)
    assert findings == []


def test_check_start_state_missing():
    lines = ["Value iface (\\S+)", "Foo"]
    findings = check_start_state(lines)
    assert "missing_start_state" in findings


def test_check_start_state_casing():
    lines = ["value iface (\\S+)", "start"]
    findings = check_start_state(lines)
    assert "start_state_casing_error: start" in findings


def test_check_start_state_multiple():
    lines = ["Start", "Foo", "Start"]
    findings = check_start_state(lines)
    assert "multiple_start_state" in findings


def test_check_start_state_preceding_newline_error():
    lines = ["Value iface (\\S+)", "Start"]
    findings = check_start_state(lines)
    assert "start_state_preceding_newline_error" in findings


# ---------------------------------------------------------
# check_transition_states
# ---------------------------------------------------------
def test_check_transition_states_forbidden():
    lines = ["Next", "Continue", "MyState"]
    findings = check_transition_states(lines)
    assert "forbidden_state_name: Next" in findings
    assert "forbidden_state_name: Continue" in findings


def test_check_transition_states_valid():
    lines = ["Start", "MyState", "OtherState"]
    findings = check_transition_states(lines)
    assert findings == []


# ---------------------------------------------------------
# check_rule_actions
# ---------------------------------------------------------
def test_check_rule_actions_valid():
    lines = ["  ^foo -> Record"]
    findings = check_rule_actions(lines)
    assert findings == []


def test_check_rule_actions_invalid_action():
    lines = ["  ^foo -> WrongAction"]
    findings = check_rule_actions(lines)
    assert any("invalid_action" in f for f in findings)


def test_check_rule_actions_invalid_rule():
    lines = ["  foo -> Record"]
    findings = check_rule_actions(lines)
    assert any("invalid_rule_definition" in f for f in findings)


def test_check_rule_actions_no_action_is_fine():
    lines = ["  ^foo"]
    findings = check_rule_actions(lines)
    assert findings == []


# ---------------------------------------------------------
# check_rule_spacers
# ---------------------------------------------------------
def test_check_rule_spacers_consistent():
    lines = ["  ^foo -> Record", "  ^bar -> Continue"]
    findings = check_rule_spacers(lines)
    assert findings == []


def test_check_rule_spacers_inconsistent():
    lines = ["  ^foo -> Record", "    ^bar -> Continue"]
    findings = check_rule_spacers(lines)
    assert any("inconsistent_rule_definition_spacers" in f for f in findings)


# ---------------------------------------------------------
# find_template_issues
# ---------------------------------------------------------
def test_find_template_issues_ready():
    template = """
Value iface (\\S+)

Start
  ^interface ${iface} -> Record
""".strip()
    sample = "interface Gi0/1"
    records = [{"iface": "Gi0/1"}]

    result = find_template_issues(template, records, sample)
    assert isinstance(result, TemplateFindingResult)
    assert result.ready is True
    assert result.findings == []


def test_find_template_issues_with_errors():
    template = """
Value iface \\S+

Start
  ^interface ${iface} -> Record
""".strip()
    sample = "interface Gi0/1"
    records = [["Gi0/1"]]

    result = find_template_issues(template, records, sample)
    assert result.ready is False
    assert len(result.findings) > 0
    assert any("invalid_value_definition" in f for f in result.findings)
