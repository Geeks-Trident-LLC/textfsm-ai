# tests/unit/generation/support/test_generator.py

from unittest.mock import MagicMock, patch

from textfsm_ai.generation.support.generator import GenerationResult, generate


def make_structured(template="RAW"):
    s = MagicMock()
    s.template = template
    s.to_dict.return_value = {"template": template}
    return s


# ------------------------------------------------------------
# 1. Raw template valid
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
def test_valid_raw(mock_val):
    mock_val.return_value = True
    structured = make_structured("RAW")

    result = generate(structured)

    assert isinstance(result, GenerationResult)
    assert result.template == "RAW"
    assert result.status == "valid_raw"
    assert result.structured is structured


# ------------------------------------------------------------
# 2. Raw invalid → cleaned valid
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
@patch("textfsm_ai.generation.support.generator.clean_template")
def test_cleaned_valid(mock_clean, mock_val):
    mock_val.side_effect = [False, True]
    mock_clean.return_value = "CLEANED"

    structured = make_structured("RAW")

    result = generate(structured)

    assert result.template == "CLEANED"
    assert result.status == "cleaned"


# ------------------------------------------------------------
# 3. Raw invalid → cleaned invalid
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
@patch("textfsm_ai.generation.support.generator.clean_template")
def test_cleaned_invalid(mock_clean, mock_val):
    mock_val.side_effect = [False, False]
    mock_clean.return_value = "CLEANED"

    structured = make_structured("RAW")

    result = generate(structured)

    assert result.template == "CLEANED"
    assert result.status == "invalid"
