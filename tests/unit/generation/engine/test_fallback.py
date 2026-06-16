# tests/unit/generation/engine/test_fallback.py

from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.generation.core.models import (
    OnePassResult,
    StructuredResult,
    TwoPassResult,
)
from textfsm_ai.generation.engine import fallback

# ------------------------------------------------------------
# Helpers to build fake dataclasses
# ------------------------------------------------------------


@pytest.fixture
def make_one():
    def _make(response=None):
        return OnePassResult(
            prompt="P1",
            response=response,
            model="m",
            provider="p",
            metadata={"llm_run": MagicMock()},
        )

    return _make


@pytest.fixture
def make_two():
    def _make(response_free=None, response_structured=None):
        return TwoPassResult(
            prompt_free="PA",
            response_free=response_free,
            prompt_structured="PB",
            response_structured=response_structured,
            model="m",
            provider="p",
            metadata={"llm_run": MagicMock()},
        )

    return _make


@pytest.fixture
def fake_structured():
    return MagicMock(spec=StructuredResult)


# ------------------------------------------------------------
# 1. Prefer two.response_structured
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_prefers_two_pass_structured(
    mock_clean, mock_parse, make_one, make_two, fake_structured
):
    two = make_two(response_free="FREE", response_structured="STRUCT")
    one = make_one(response="ONE")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("STRUCT")
    mock_parse.assert_called_once_with("CLEANED", two)
    assert result is fake_structured


# ------------------------------------------------------------
# 2. Else use two.response_free
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_uses_two_pass_free(
    mock_clean, mock_parse, make_one, make_two, fake_structured
):
    two = make_two(response_free="FREE", response_structured=None)
    one = make_one(response="ONE")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("FREE")
    mock_parse.assert_called_once_with("CLEANED", two)
    assert result is fake_structured


# ------------------------------------------------------------
# 3. Else use one.response
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_uses_one_pass_response(
    mock_clean, mock_parse, make_one, make_two, fake_structured
):
    two = make_two(response_free=None, response_structured=None)
    one = make_one(response="ONE")

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("ONE")
    mock_parse.assert_called_once_with("CLEANED", one)
    assert result is fake_structured


# ------------------------------------------------------------
# 4. Else synthesize empty
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_synthesizes_empty(mock_clean, mock_parse, make_one, make_two, fake_structured):
    two = make_two(response_free=None, response_structured=None)
    one = make_one(response=None)

    mock_clean.return_value = "CLEANED"
    mock_parse.return_value = fake_structured

    result = fallback.run(one, two)

    mock_clean.assert_called_once_with("")

    cleaned_raw, base = mock_parse.call_args.args
    assert cleaned_raw == "CLEANED"
    assert base is one  # one_pass_result preferred as base

    assert result is fake_structured


# ------------------------------------------------------------
# 5. clean_template raises → propagate
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_clean_template_raises(mock_clean, mock_parse, make_one, make_two):
    two = make_two(response_free=None, response_structured=None)
    one = make_one(response="ONE")

    mock_clean.side_effect = Exception("clean error")

    with pytest.raises(Exception):
        fallback.run(one, two)

    mock_clean.assert_called_once_with("ONE")
    mock_parse.assert_not_called()


# ------------------------------------------------------------
# 6. parse_from_response raises → propagate
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.fallback.parse_from_response")
@patch("textfsm_ai.generation.engine.fallback.clean_template")
def test_parse_from_response_raises(mock_clean, mock_parse, make_one, make_two):
    two = make_two(response_free=None, response_structured=None)
    one = make_one(response="ONE")

    mock_clean.return_value = "CLEANED"
    mock_parse.side_effect = Exception("parse error")

    with pytest.raises(Exception):
        fallback.run(one, two)
