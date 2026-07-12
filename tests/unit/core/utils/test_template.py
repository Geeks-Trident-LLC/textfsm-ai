# tests/unit/core/utils/test_template.py

import pytest

from textfsm_ai.core.utils import template

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
VALID_TEMPLATE = r"""
Value iface (\S+)
Value desc (.+)

Start
  ^interface ${iface} -> Continue
  ^ description: ${desc} -> Record
""".strip()

SAMPLE_SINGLE = """\
interface Gi0/1
 description: Uplink
"""

SAMPLE_MULTI = """\
interface Gi0/1
 description: Uplink
interface Gi0/2
 description: Downlink
"""


# ---------------------------------------------------------
# parse_to_lists
# ---------------------------------------------------------
def test_parse_to_lists_single_record():
    rows = template.parse_to_lists(VALID_TEMPLATE, SAMPLE_SINGLE)

    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0] == ["Gi0/1", "Uplink"]


def test_parse_to_lists_multiple_records():
    rows = template.parse_to_lists(VALID_TEMPLATE, SAMPLE_MULTI)

    assert len(rows) == 2
    assert rows[0] == ["Gi0/1", "Uplink"]
    assert rows[1] == ["Gi0/2", "Downlink"]


def test_parse_to_lists_invalid_template():
    bad_template = "Value iface (\\S+)\nStart\n  ^ -> Record"

    with pytest.raises(Exception):
        template.parse_to_lists(bad_template, SAMPLE_SINGLE)


# ---------------------------------------------------------
# parse_to_dicts
# ---------------------------------------------------------
def test_parse_to_dicts_single_record():
    rows = template.parse_to_dicts(VALID_TEMPLATE, SAMPLE_SINGLE)

    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0] == {"iface": "Gi0/1", "desc": "Uplink"}


def test_parse_to_dicts_multiple_records():
    rows = template.parse_to_dicts(VALID_TEMPLATE, SAMPLE_MULTI)

    assert len(rows) == 2
    assert rows[0] == {"iface": "Gi0/1", "desc": "Uplink"}
    assert rows[1] == {"iface": "Gi0/2", "desc": "Downlink"}


def test_parse_to_dicts_invalid_template():
    bad_template = "Value iface (\\S+)\nStart\n  ^ -> Record"

    with pytest.raises(Exception):
        template.parse_to_dicts(bad_template, SAMPLE_SINGLE)


# ---------------------------------------------------------
# validate_template
# ---------------------------------------------------------
def test_validate_template_empty_string():
    result = template.validate_template("")

    assert result.ready is False
    assert result.reason == "template_empty"
    assert result.data == ""


def test_validate_template_whitespace_only():
    result = template.validate_template("   \n\t  ")

    assert result.ready is False
    assert result.reason == "template_empty"


def test_validate_template_valid_template():
    result = template.validate_template(VALID_TEMPLATE)

    assert result.ready is True
    assert result.reason == ""
    assert result.data == VALID_TEMPLATE


def test_validate_template_syntax_error():
    bad_template = "Value iface (\\S+)\nStart\n  ^ -> Record"

    result = template.validate_template(bad_template)

    assert result.ready is False
    assert result.data == bad_template
    assert result.reason.startswith("template_syntax_error: ")
