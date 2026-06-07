from unittest.mock import MagicMock, patch

from textfsm_ai.generation import fallback
from textfsm_ai.generation.extractor import LLMRunResult
from textfsm_ai.generation.structured_extractor import StructuredResult


# ------------------------------------------------------------
# Helper to create LLMRunResult
# ------------------------------------------------------------
def make_llm(provider="p", model="m", response=None, next_response=None):
    llm = LLMRunResult(
        provider=provider,
        model=model,
        sample="s",
        prompt="p",
        response=response,
        next_response=next_response,
    )
    return llm


# ------------------------------------------------------------
# 1. Prefer two_pass.next_response
# ------------------------------------------------------------
@patch("textfsm_ai.generation.fallback.parse_from_response")
@patch("textfsm_ai.generation.fallback.clean_template")
def test_fallback_prefers_two_pass_next_response(mock_clean, mock_parse):
    two = make_llm(response="R2", next_response="NEXT2")
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = MagicMock(spec=StructuredResult)

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("NEXT2")
    mock_parse.assert_called_once_with("CLEANED", two)

    assert result is mock_parse.return_value


# ------------------------------------------------------------
# 2. Else use two_pass.response
# ------------------------------------------------------------
@patch("textfsm_ai.generation.fallback.parse_from_response")
@patch("textfsm_ai.generation.fallback.clean_template")
def test_fallback_uses_two_pass_response(mock_clean, mock_parse):
    two = make_llm(response="R2", next_response=None)
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = MagicMock(spec=StructuredResult)

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("R2")
    mock_parse.assert_called_once_with("CLEANED", two)

    assert result is mock_parse.return_value


# ------------------------------------------------------------
# 3. Else use one_pass.response
# ------------------------------------------------------------
@patch("textfsm_ai.generation.fallback.parse_from_response")
@patch("textfsm_ai.generation.fallback.clean_template")
def test_fallback_uses_one_pass_response(mock_clean, mock_parse):
    two = make_llm(response=None, next_response=None)
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = MagicMock(spec=StructuredResult)

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("R1")
    mock_parse.assert_called_once_with("CLEANED", one)

    assert result is mock_parse.return_value


# ------------------------------------------------------------
# 4. Else synthesize empty fallback LLMRunResult
# ------------------------------------------------------------
@patch("textfsm_ai.generation.fallback.parse_from_response")
@patch("textfsm_ai.generation.fallback.clean_template")
def test_fallback_synthesizes_empty(mock_clean, mock_parse):
    # No usable responses
    two = make_llm(response=None, next_response=None)
    one = make_llm(response=None, next_response=None)

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = MagicMock(spec=StructuredResult)

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("")  # empty candidate_raw

    # parse_from_response should receive CLEANED and base = one_pass_result
    args, kwargs = mock_parse.call_args
    cleaned_raw, base = args

    assert cleaned_raw == "CLEANED"
    assert base is one  # IMPORTANT: fallback uses one_pass_result, not synthesized

    assert result is mock_parse.return_value
