# tests/unit/generation/support/test_generator.py

from unittest.mock import patch

from textfsm_ai.generation.support.extractor import LLMRunResult
from textfsm_ai.generation.support.generator import (
    GenerationResult,
    generate,
)
from textfsm_ai.generation.support.structured_extractor import StructuredResult

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_structured(template: str):
    """Create a StructuredResult with minimal valid fields."""
    llm = LLMRunResult(
        provider="deepseek",
        model="deepseek-chat",
        sample="sample",
        prompt="prompt",
        response="response",
    )
    return StructuredResult(
        template=template,
        data={"textfsm_template": template},
        llm_run_result=llm,
    )


# ------------------------------------------------------------
# valid_raw branch
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
@patch("textfsm_ai.generation.support.generator.clean_template")
def test_generate_valid_raw(mock_clean, mock_validate):
    mock_validate.side_effect = [True]  # raw is valid

    structured = make_structured("VALID_TEMPLATE")

    result = generate(structured)

    assert isinstance(result, GenerationResult)
    assert result.status == "valid_raw"
    assert result.template == "VALID_TEMPLATE"
    assert result.structured is structured
    assert result.is_success()
    assert not result.is_failure()

    # clean_template should NOT be called
    mock_clean.assert_not_called()


# ------------------------------------------------------------
# cleaned branch
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
@patch("textfsm_ai.generation.support.generator.clean_template")
def test_generate_cleaned(mock_clean, mock_validate):
    mock_validate.side_effect = [False, True]  # raw invalid, cleaned valid
    mock_clean.return_value = "CLEANED_TEMPLATE"

    structured = make_structured("RAW_INVALID")

    result = generate(structured)

    assert result.status == "cleaned"
    assert result.template == "CLEANED_TEMPLATE"
    assert result.structured is structured
    assert result.is_success()
    assert not result.is_failure()

    mock_clean.assert_called_once_with("RAW_INVALID")


# ------------------------------------------------------------
# invalid branch
# ------------------------------------------------------------


@patch("textfsm_ai.generation.support.generator.validate_template")
@patch("textfsm_ai.generation.support.generator.clean_template")
def test_generate_invalid(mock_clean, mock_validate):
    mock_validate.side_effect = [False, False]  # raw invalid, cleaned invalid
    mock_clean.return_value = "STILL_INVALID"

    structured = make_structured("RAW_INVALID")

    result = generate(structured)

    assert result.status == "invalid"
    assert result.template == "STILL_INVALID"
    assert result.structured is structured
    assert not result.is_success()
    assert result.is_failure()

    mock_clean.assert_called_once_with("RAW_INVALID")


# ------------------------------------------------------------
# to_dict() behavior
# ------------------------------------------------------------


def test_generation_result_to_dict():
    structured = make_structured("TEMPLATE")
    result = GenerationResult(
        template="TEMPLATE",
        status="valid_raw",
        structured=structured,
    )

    d = result.to_dict()

    assert d["template"] == "TEMPLATE"
    assert d["status"] == "valid_raw"
    assert d["structured"] is structured
