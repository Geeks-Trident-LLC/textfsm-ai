# tests/unit/generation/support/test_validator.py

from textfsm_ai.generation.support.validator import (
    HandlingTemplateValidator,
    ParsedResultValidator,
    TemplateValidator,
    VariableExplanationValidator,
    is_ascii,
    validate_template,
)

# ------------------------------------------------------------
# TemplateValidator tests
# ------------------------------------------------------------


def test_template_validator_valid_template():
    template = """
Value interface_name (\\S+)

Start
  ^interface ${interface_name} -> Record
""".strip()
    assert TemplateValidator.is_valid_template(template) is True
    assert validate_template(template) is True


def test_template_validator_missing_start():
    template = """
Value interface_name (\\S+)
  ^interface ${interface_name} -> Record
"""
    assert TemplateValidator.is_valid_template(template) is False


def test_template_validator_invalid_syntax():
    # Missing closing brace or malformed regex
    template = """
Value interface_name (\\S+

Start
  ^interface ${interface_name} -> Record
"""
    assert TemplateValidator.is_valid_template(template) is False


def test_template_validator_empty_or_non_string():
    assert TemplateValidator.is_valid_template("") is False
    assert TemplateValidator.is_valid_template("   ") is False
    assert TemplateValidator.is_valid_template(None) is False
    assert TemplateValidator.is_valid_template(123) is False


# ------------------------------------------------------------
# ParsedResultValidator tests
# ------------------------------------------------------------


def test_parsed_result_validator_valid():
    parsed = [{"a": 1}, {"b": 2}]
    assert ParsedResultValidator.is_valid(parsed) is True


def test_parsed_result_validator_invalid_not_list():
    assert ParsedResultValidator.is_valid({"a": 1}) is False


def test_parsed_result_validator_invalid_item_not_dict():
    parsed = [{"a": 1}, "not a dict"]
    assert ParsedResultValidator.is_valid(parsed) is False


# ------------------------------------------------------------
# is_ascii tests
# ------------------------------------------------------------


def test_is_ascii_valid():
    assert is_ascii("hello") is True
    assert is_ascii("GigabitEthernet0/1") is True


def test_is_ascii_invalid():
    assert is_ascii("café") is False
    assert is_ascii("接口") is False


# ------------------------------------------------------------
# VariableExplanationValidator tests
# ------------------------------------------------------------


def test_variable_explanation_validator_valid():
    expl = {"interface_name": "ASCII only explanation"}
    assert VariableExplanationValidator.is_valid(expl) is True


def test_variable_explanation_validator_invalid_non_dict():
    assert VariableExplanationValidator.is_valid("not a dict") is False


def test_variable_explanation_validator_invalid_key_or_value():
    expl = {"": "valid", "name": ""}
    assert VariableExplanationValidator.is_valid(expl) is False


def test_variable_explanation_validator_invalid_non_ascii():
    expl = {"interface": "café"}
    assert VariableExplanationValidator.is_valid(expl) is False


# ------------------------------------------------------------
# HandlingTemplateValidator tests
# ------------------------------------------------------------


def test_handling_template_validator_valid():
    lines = ["This is ASCII.", "Another ASCII line."]
    assert HandlingTemplateValidator.is_valid(lines) is True


def test_handling_template_validator_invalid_not_list():
    assert HandlingTemplateValidator.is_valid("not a list") is False


def test_handling_template_validator_invalid_item_not_string():
    assert HandlingTemplateValidator.is_valid(["ok", 123]) is False


def test_handling_template_validator_invalid_non_ascii():
    assert HandlingTemplateValidator.is_valid(["valid", "café"]) is False
