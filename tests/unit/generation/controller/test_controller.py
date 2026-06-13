# tests/unit/generation/controller/test_controller.py

from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.generation.controller.controller import Controller
from textfsm_ai.generation.support.generator import GenerationResult

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------


@pytest.fixture
def ctrl():
    return Controller(api_key="KEY", model="MODEL", max_retries=2)


@pytest.fixture
def fake_result():
    def _make(status="valid_raw"):
        return GenerationResult(
            template="TEMPLATE",
            status=status,
            structured=MagicMock(),
        )

    return _make


# ------------------------------------------------------------
# 1. ONE-PASS success
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.controller.generator.generate")
@patch("textfsm_ai.generation.controller.controller.validate_template")
@patch("textfsm_ai.generation.controller.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.controller.one_pass.run")
def test_one_pass_success(
    mock_one_pass,
    mock_parse,
    mock_validate,
    mock_generate,
    ctrl,
    fake_result,
):
    # Arrange
    one = MagicMock(response="RAW1", next_response=None)
    mock_one_pass.return_value = one

    structured = MagicMock(template="VALID")
    mock_parse.return_value = structured

    mock_validate.return_value = True
    mock_generate.return_value = fake_result("valid_raw")

    # Act
    result = ctrl.run("sample")

    # Assert
    mock_one_pass.assert_called_once()
    mock_parse.assert_called_once_with("RAW1", one)
    mock_validate.assert_called_once_with("VALID")
    mock_generate.assert_called_once_with(structured)

    assert isinstance(result, GenerationResult)
    assert result.status == "valid_raw"


# ------------------------------------------------------------
# 2. TWO-PASS success after ONE-PASS fails
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.controller.generator.generate")
@patch("textfsm_ai.generation.controller.controller.validate_template")
@patch("textfsm_ai.generation.controller.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.controller.two_pass.run")
@patch("textfsm_ai.generation.controller.controller.one_pass.run")
def test_two_pass_success(
    mock_one_pass,
    mock_two_pass,
    mock_parse,
    mock_validate,
    mock_generate,
    ctrl,
    fake_result,
):
    # Arrange
    mock_one_pass.return_value = MagicMock(response="RAW1", next_response=None)
    mock_two_pass.return_value = MagicMock(response="RAW2", next_response=None)

    structured_invalid = MagicMock(template="INVALID")
    structured_valid = MagicMock(template="VALID")

    mock_parse.side_effect = [
        structured_invalid,  # one-pass #1
        structured_invalid,  # one-pass #2
        structured_valid,  # two-pass #1
    ]

    mock_validate.side_effect = [False, False, True]

    mock_generate.return_value = fake_result("valid_raw")

    # Act
    result = ctrl.run("sample")

    # Assert
    assert mock_one_pass.call_count == 2
    assert mock_two_pass.call_count == 1

    mock_generate.assert_called_once_with(structured_valid)
    assert result.status == "valid_raw"


# ------------------------------------------------------------
# 3. FALLBACK success after both ONE-PASS and TWO-PASS fail
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.controller.generator.generate")
@patch("textfsm_ai.generation.controller.controller.fallback.run")
@patch("textfsm_ai.generation.controller.controller.validate_template")
@patch("textfsm_ai.generation.controller.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.controller.two_pass.run")
@patch("textfsm_ai.generation.controller.controller.one_pass.run")
def test_fallback_success(
    mock_one_pass,
    mock_two_pass,
    mock_parse,
    mock_validate,
    mock_fallback,
    mock_generate,
    ctrl,
    fake_result,
):
    # Arrange
    one = MagicMock(response="RAW1", next_response=None)
    two = MagicMock(response="RAW2", next_response=None)

    mock_one_pass.return_value = one
    mock_two_pass.return_value = two

    structured_invalid = MagicMock(template="INVALID")
    mock_parse.return_value = structured_invalid
    mock_validate.return_value = False

    fb_structured = MagicMock()
    mock_fallback.return_value = fb_structured

    mock_generate.return_value = fake_result("cleaned")

    # Act
    result = ctrl.run("sample")

    # Assert
    assert mock_one_pass.call_count == 2
    assert mock_two_pass.call_count == 2

    mock_fallback.assert_called_once_with(one, two)
    mock_generate.assert_called_once_with(fb_structured)

    assert result.status == "cleaned"
