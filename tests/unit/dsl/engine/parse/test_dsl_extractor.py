# tests/unit/dsl/engine/parse/test_dsl_extractor.py

from unittest.mock import MagicMock, patch

from textfsm_ai.dsl.core.models import DSLExtractorResult
from textfsm_ai.dsl.engine.parse.dsl_extractor import DSLExtractor, extract_machine_dsl

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_pattern(regex):
    """Mock Pattern object with .regex attribute."""
    m = MagicMock()
    m.regex = regex
    return m


# ------------------------------------------------------------
# Test: Value line parsing
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.dsl_extractor.create_node")
@patch(
    "textfsm_ai.dsl.engine.parse.dsl_extractor.PATTERNS",
    {
        "word": make_pattern(r"\S+"),
        "GREEDY": make_pattern(r".+"),
    },
)
def test_parse_value_success(mock_create_node):
    mock_node = MagicMock()
    mock_node.to_expression.return_value = "${iface}"
    mock_node.to_expression_regex.return_value = r"\S+"
    mock_create_node.return_value = mock_node

    template = "Value iface (\\S+)"
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert result.ready
    assert len(result.variables) == 1

    var = result.variables[0]
    assert var["name"] == "iface"
    assert var["keyword"] == "word"
    assert var["expression"] == "${iface}"
    assert var["expression_regex"] == r"\S+"


# ------------------------------------------------------------
# Test: Unknown regex pattern
# ------------------------------------------------------------


@patch(
    "textfsm_ai.dsl.engine.parse.dsl_extractor.PATTERNS", {"WORD": make_pattern(r"\S+")}
)
def test_parse_value_unknown_pattern():
    template = "Value iface ([A-Z]+)"  # not in PATTERNS
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert not result.ready
    assert "RuntimeError: Unknown regex pattern" in result.reason


# ------------------------------------------------------------
# Test: State parsing
# ------------------------------------------------------------


def test_parse_state_success():
    template = "Start"
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert result.ready
    assert len(result.states) == 1
    assert result.states[0]["name"] == "Start"
    assert result.states[0]["transitions"] == []


# ------------------------------------------------------------
# Test: Transition parsing
# ------------------------------------------------------------


def test_parse_transition_success():
    template = """
Start
  ^interface ${iface} -> Continue
"""
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert result.ready
    assert len(result.states) == 1

    transitions = result.states[0]["transitions"]
    assert len(transitions) == 1
    assert transitions[0]["pattern"] == "^interface ${iface}"
    assert transitions[0]["action"] == "Continue"


# ------------------------------------------------------------
# Test: Multiple states + transitions
# ------------------------------------------------------------


def test_parse_multiple_states():
    template = """
Start
  ^foo -> Next

Next
  ^bar -> Record
"""
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert result.ready
    assert len(result.states) == 2

    assert result.states[0]["name"] == "Start"
    assert result.states[1]["name"] == "Next"

    assert result.states[0]["transitions"][0]["pattern"] == "^foo"
    assert result.states[1]["transitions"][0]["pattern"] == "^bar"


# ------------------------------------------------------------
# Test: _parse_value exception handling
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.dsl_extractor.create_node")
@patch(
    "textfsm_ai.dsl.engine.parse.dsl_extractor.PATTERNS", {"WORD": make_pattern(r"\S+")}
)
def test_parse_value_exception(mock_create_node):
    mock_create_node.side_effect = RuntimeError("boom")
    template = "Value iface (\\S+)"
    extractor = DSLExtractor(template)
    result = extractor.extract()

    assert not result.ready
    assert "RuntimeError" in result.reason


# ------------------------------------------------------------
# Test: extract_machine_dsl wrapper
# ------------------------------------------------------------


def test_extract_machine_dsl_wrapper():
    template = "Start"
    result = extract_machine_dsl(template)

    assert isinstance(result, DSLExtractorResult)
    assert result.ready
    assert len(result.states) == 1
