# tests/unit/generation/support/test_validator2.py

from textfsm_ai.generation.support.validator import validate_template_and_records

VALID_TEMPLATE = r"""
Value iface (\S+)
Value desc (.+)

Start
  ^interface ${iface} -> Continue
  ^ description: ${desc} -> Record
""".strip()

SAMPLE = """\
interface Gi0/1
 description: Uplink
"""

EXPECTED = [{"iface": "Gi0/1", "desc": "Uplink"}]


# ---------------------------------------------------------
# Syntax error
# ---------------------------------------------------------
def test_syntax_error():
    bad_template = "Value iface (\\S+)\nStart\n  ^ -> Record"
    findings, ready = validate_template_and_records(bad_template, SAMPLE, EXPECTED)

    assert ready is False
    assert any("template_syntax_error" in f for f in findings)


# ---------------------------------------------------------
# Parse error
# ---------------------------------------------------------
def test_parse_error():
    template = VALID_TEMPLATE
    sample = "this will not match anything"

    findings, ready = validate_template_and_records(template, sample, EXPECTED)

    assert ready is False
    assert any("row_count_mismatch" in f for f in findings)


# ---------------------------------------------------------
# Perfect match
# ---------------------------------------------------------
def test_perfect_match():
    findings, ready = validate_template_and_records(VALID_TEMPLATE, SAMPLE, EXPECTED)

    assert ready is True
    assert findings == []


# ---------------------------------------------------------
# Row count mismatch
# ---------------------------------------------------------
def test_row_count_mismatch():
    expected = [
        {"iface": "Gi0/1", "desc": "Uplink"},
        {"iface": "Gi0/2", "desc": "Downlink"},
    ]

    findings, ready = validate_template_and_records(VALID_TEMPLATE, SAMPLE, expected)

    assert ready is False
    assert any("row_count_mismatch" in f for f in findings)


# ---------------------------------------------------------
# Missing key
# ---------------------------------------------------------
def test_missing_key():
    expected = [{"iface": "Gi0/1"}]  # missing desc

    findings, ready = validate_template_and_records(VALID_TEMPLATE, SAMPLE, expected)

    assert ready is False
    assert any("unexpected_key" in f for f in findings)


# ---------------------------------------------------------
# Unexpected key
# ---------------------------------------------------------
def test_unexpected_key():
    expected = [{"iface": "Gi0/1", "desc": "Uplink", "extra": "X"}]

    findings, ready = validate_template_and_records(VALID_TEMPLATE, SAMPLE, expected)
    assert ready is False
    assert any("missing_key" in f for f in findings)


# ---------------------------------------------------------
# Uppercase variable name
# ---------------------------------------------------------
def test_uppercase_variable_name():
    template = r"""
Value IFACE (\S+)

Start
  ^interface ${IFACE} -> Record
""".strip()
    sample = "interface Gi0/1"
    expected = [{"iface": "Gi0/1"}]

    findings, ready = validate_template_and_records(template, sample, expected)

    assert ready is False
    assert any("invalid_variable_case" in f for f in findings)


# ---------------------------------------------------------
# Value mismatch
# ---------------------------------------------------------
def test_value_mismatch():
    expected = [{"iface": "Gi0/2", "desc": "Uplink"}]  # iface mismatch

    findings, ready = validate_template_and_records(VALID_TEMPLATE, SAMPLE, expected)

    assert ready is False
    assert any("value_mismatch" in f for f in findings)
