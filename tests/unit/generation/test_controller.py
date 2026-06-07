from unittest.mock import MagicMock, patch

from textfsm_ai.generation.controller import Controller
from textfsm_ai.generation.generator import GenerationResult


# ------------------------------------------------------------
# Helper: make a fake GenerationResult
# ------------------------------------------------------------
def make_result(status="valid_raw"):
    return GenerationResult(
        template="TEMPLATE",
        status=status,
        structured=MagicMock(),
    )


# ------------------------------------------------------------
# 1. ONE-PASS success
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.generator.generate")
@patch("textfsm_ai.generation.controller.validate_template")
@patch("textfsm_ai.generation.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.one_pass.run")
def test_controller_one_pass_success(
    mock_one_pass,
    mock_parse,
    mock_validate,
    mock_generate,
):
    ctrl = Controller(api_key="KEY", model="MODEL", max_retries=2)

    # Fake one-pass LLMRunResult
    one = MagicMock()
    one.response = "RAW1"
    one.next_response = None
    mock_one_pass.return_value = one

    # parse_from_response returns a structured object
    structured = MagicMock()
    structured.template = "VALID_TEMPLATE"
    mock_parse.return_value = structured

    # validate_template returns True immediately
    mock_validate.return_value = True

    # generator.generate returns a GenerationResult
    mock_generate.return_value = make_result("valid_raw")

    result = ctrl.run("sample")

    # Assertions
    mock_one_pass.assert_called()  # at least once
    mock_parse.assert_called_with("RAW1", one)
    mock_validate.assert_called_with("VALID_TEMPLATE")
    mock_generate.assert_called_once_with(structured)

    assert isinstance(result, GenerationResult)
    assert result.status == "valid_raw"


# ------------------------------------------------------------
# 2. TWO-PASS success after ONE-PASS fails
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.generator.generate")
@patch("textfsm_ai.generation.controller.validate_template")
@patch("textfsm_ai.generation.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.two_pass.run")
@patch("textfsm_ai.generation.controller.one_pass.run")
def test_controller_two_pass_success(
    mock_one_pass,
    mock_two_pass,
    mock_parse,
    mock_validate,
    mock_generate,
):
    ctrl = Controller(api_key="KEY", model="MODEL", max_retries=2)

    # ONE-PASS always invalid
    one = MagicMock()
    one.response = "RAW1"
    one.next_response = None
    mock_one_pass.return_value = one

    # TWO-PASS returns valid
    two = MagicMock()
    two.response = "RAW2"
    two.next_response = None
    mock_two_pass.return_value = two

    # parse_from_response returns structured objects
    structured_one = MagicMock()
    structured_one.template = "INVALID_TEMPLATE"
    structured_two = MagicMock()
    structured_two.template = "VALID_TEMPLATE"

    mock_parse.side_effect = [structured_one, structured_one, structured_two]

    # validate_template: first two false, then true
    mock_validate.side_effect = [False, False, True]

    mock_generate.return_value = make_result("valid_raw")

    result = ctrl.run("sample")

    # Assertions
    assert mock_one_pass.call_count == 2
    assert mock_two_pass.call_count >= 1
    mock_generate.assert_called_once_with(structured_two)

    assert result.status == "valid_raw"


# ------------------------------------------------------------
# 3. FALLBACK success after both ONE-PASS and TWO-PASS fail
# ------------------------------------------------------------
@patch("textfsm_ai.generation.controller.generator.generate")
@patch("textfsm_ai.generation.controller.fallback.run")
@patch("textfsm_ai.generation.controller.validate_template")
@patch("textfsm_ai.generation.controller.parse_from_response")
@patch("textfsm_ai.generation.controller.two_pass.run")
@patch("textfsm_ai.generation.controller.one_pass.run")
def test_controller_fallback_success(
    mock_one_pass,
    mock_two_pass,
    mock_parse,
    mock_validate,
    mock_fallback,
    mock_generate,
):
    ctrl = Controller(api_key="KEY", model="MODEL", max_retries=2)

    # ONE-PASS always invalid
    one = MagicMock()
    one.response = "RAW1"
    one.next_response = None
    mock_one_pass.return_value = one

    # TWO-PASS always invalid
    two = MagicMock()
    two.response = "RAW2"
    two.next_response = None
    mock_two_pass.return_value = two

    # parse_from_response always returns invalid structured
    structured_invalid = MagicMock()
    structured_invalid.template = "INVALID"
    mock_parse.return_value = structured_invalid

    # validate_template always false
    mock_validate.return_value = False

    # fallback returns a structured object
    fb_structured = MagicMock()
    mock_fallback.return_value = fb_structured

    mock_generate.return_value = make_result("cleaned")

    result = ctrl.run("sample")

    # Assertions
    assert mock_one_pass.call_count == 2
    assert mock_two_pass.call_count == 2
    mock_fallback.assert_called_once_with(one, two)
    mock_generate.assert_called_once_with(fb_structured)

    assert result.status == "cleaned"
