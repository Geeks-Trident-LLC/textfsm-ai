# tests/unit/dsl/engine/parse/test_template_canonicalizer.py

from unittest.mock import MagicMock, patch

from textfsm_ai.dsl.engine.parse.template_canonicalizer import canonicalize

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_validator(ready=True, reason=""):
    m = MagicMock()
    m.ready = ready
    m.reason = reason
    return m


# ------------------------------------------------------------
# Test: VALUE line normalization
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_basic_value_line(mock_infer, mock_validate):
    mock_infer.return_value = {
        "iface": {"regex": r"\S+"},
    }
    mock_validate.return_value = make_validator(ready=True)

    template = "Value iface (.*)"
    result = canonicalize(template, records=[{}])

    assert result.ready is True
    assert result.return_text == "Value iface (\\S+)"


# ------------------------------------------------------------
# Test: variable name lowercasing
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_lowercase_varname(mock_infer, mock_validate):
    mock_infer.return_value = {
        "iface": {"regex": r"\S+"},
    }
    mock_validate.return_value = make_validator(ready=True)

    template = "Value IFACE (.*)"
    result = canonicalize(template, records=[{}])

    assert "Value iface (" in result.return_text


# ------------------------------------------------------------
# Test: option sorting
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_option_sorting(mock_infer, mock_validate):
    mock_infer.return_value = {
        "iface": {"regex": r"\S+"},
    }
    mock_validate.return_value = make_validator(ready=True)

    template = "Value Key,Required iface (.*)"
    result = canonicalize(template, records=[{}])

    # Sorted alphabetically: Key,Required → Required,Key
    assert (
        result.return_text == "Value Key,Required iface (\\S+)"
        or result.return_text == "Value Required,Key iface (\\S+)"
    )


# ------------------------------------------------------------
# Test: variable not in mapping → passthrough
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_missing_variable(mock_infer, mock_validate):
    mock_infer.return_value = {}  # no variables known
    mock_validate.return_value = make_validator(ready=True)

    template = "Value iface (.*)"
    result = canonicalize(template, records=[{}])

    # Should not modify the line
    assert result.return_text == "Value iface (.*)"


# ------------------------------------------------------------
# Test: validator failure
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_validator_failure(mock_infer, mock_validate):
    mock_infer.return_value = {
        "iface": {"regex": r"\S+"},
    }
    mock_validate.return_value = make_validator(ready=False, reason="invalid template")

    template = "Value iface (.*)"
    result = canonicalize(template, records=[{}])

    assert result.ready is False
    assert result.reason == "invalid template"
    assert "Value iface (\\S+)" in result.return_text


# ------------------------------------------------------------
# Test: multi-line template
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.validate_template")
@patch("textfsm_ai.dsl.engine.parse.template_canonicalizer.infer_variable_mapping")
def test_canonicalize_multiline(mock_infer, mock_validate):
    mock_infer.return_value = {
        "iface": {"regex": r"\S+"},
        "mtu": {"regex": r"\d+"},
    }
    mock_validate.return_value = make_validator(ready=True)

    template = """
Value iface (.*)
Value mtu (.*)
Start
  ^foo -> Record
""".strip()

    result = canonicalize(template, records=[{}])

    assert "Value iface (\\S+)" in result.return_text
    assert "Value mtu (\\d+)" in result.return_text
    assert "Start" in result.return_text
    assert "^foo" in result.return_text
