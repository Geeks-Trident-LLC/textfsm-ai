# tests/unit/generation/engine/test_generation_engine.py

from unittest.mock import patch

import textfsm_ai.generation.engine.generation_engine as gen_engine
from textfsm_ai.generation.core.models import (
    FallbackResult,
    OnePassResult,
    TwoPassResult,
)


@patch("textfsm_ai.generation.engine.generation_engine._run_one_pass")
def test_one_pass(mock_run):
    mock_run.return_value = OnePassResult("P", "R", "M", "LLM")

    result = gen_engine.one_pass("KEY", "M", "S")

    mock_run.assert_called_once_with(api_key="KEY", model="M", sample="S")
    assert isinstance(result, OnePassResult)


@patch("textfsm_ai.generation.engine.generation_engine._run_two_pass")
def test_two_pass(mock_run):
    mock_run.return_value = TwoPassResult("A", "B", "C", "D", "M", "LLM")

    result = gen_engine.two_pass("KEY", "M", "S")

    mock_run.assert_called_once_with(api_key="KEY", model="M", sample="S")
    assert isinstance(result, TwoPassResult)


@patch("textfsm_ai.generation.engine.generation_engine._run_fallback")
def test_fallback(mock_fb):
    one = OnePassResult("P", "R", "M", "LLM")
    two = TwoPassResult("A", "B", "C", "D", "M", "LLM")

    mock_fb.return_value = FallbackResult("one_pass", "reason", one)

    result = gen_engine.fallback(one, two)

    mock_fb.assert_called_once_with(one, two)
    assert isinstance(result, FallbackResult)
