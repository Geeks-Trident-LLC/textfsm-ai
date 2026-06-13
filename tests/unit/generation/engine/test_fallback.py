# tests/unit/generation/engine/test_fallback.py

from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.generation.engine import fallback
from textfsm_ai.generation.support.extractor import LLMRunResult
from textfsm_ai.generation.support.structured_extractor import StructuredResult

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------


@pytest.fixture
def make_llm():
    def _make(provider="p", model="m", response=None, next_response=None):
        return LLMRunResult(
            provider=provider,
            model=model,
            sample="s",
            prompt="p",
            response=response,
            next_response=next_response,
        )

    return _make


@pytest.fixture
def fake_structured():
    return MagicMock(spec=StructuredResult)


# ------------------------------------------------------------
# 1. Prefer two_pass.next_response
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_prefers_two_pass_next_response(
    mock_clean, mock_parse, make_llm, fake_structured
):
    two = make_llm(response="R2", next_response="NEXT2")
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("NEXT2")
    mock_parse.assert_called_once_with("CLEANED", two)
    assert result is fake_structured


# ------------------------------------------------------------
# 2. Else use one_pass.response (two_pass.response is no longer used)
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_uses_one_pass_response(mock_clean, mock_parse, make_llm, fake_structured):
    two = make_llm(response="R2", next_response=None)  # ignored now
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("R1")
    mock_parse.assert_called_once_with("CLEANED", one)
    assert result is fake_structured


# ------------------------------------------------------------
# 3. Else synthesize empty fallback LLMRunResult
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_synthesizes_empty(mock_clean, mock_parse, make_llm, fake_structured):
    two = make_llm(response=None, next_response=None)
    one = make_llm(response=None, next_response=None)

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("")

    cleaned_raw, base = mock_parse.call_args.args
    assert cleaned_raw == "CLEANED"
    assert base is one  # one_pass_result is preferred as base

    assert result is fake_structured


# ------------------------------------------------------------
# 4. clean_template raises → fallback propagates error
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_clean_template_raises(mock_clean, mock_parse, make_llm):
    two = make_llm(response="R2", next_response=None)
    one = make_llm(response="R1")

    mock_clean.side_effect = Exception("clean error")

    with pytest.raises(Exception):
        fallback.run(one, two)

    mock_clean.assert_called_once_with("R1")
    mock_parse.assert_not_called()


# ------------------------------------------------------------
# 5. parse_from_response raises → fallback propagates error
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_parse_from_response_raises(mock_clean, mock_parse, make_llm):
    two = make_llm(response="R2", next_response=None)
    one = make_llm(response="R1")

    mock_clean.return_value = "CLEANED"
    mock_parse.side_effect = Exception("parse error")

    with pytest.raises(Exception):
        fallback.run(one, two)
