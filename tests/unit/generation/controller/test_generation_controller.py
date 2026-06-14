# tests/unit/generation/controller/test_generation_controller.py

from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.generation.controller.generation_controller import (
    GenerationController,
)
from textfsm_ai.generation.core.models import (
    OnePassResult,
    TwoPassResult,
)


@pytest.mark.skip(reason="Deferred: inspect this test later.")
@patch("textfsm_ai.generation.controller.generation_controller.one_pass")
@patch("textfsm_ai.generation.controller.generation_controller.parse_from_response")
@patch("textfsm_ai.generation.controller.generation_controller.validate_template")
@patch("textfsm_ai.generation.controller.generation_controller.generator")
def test_controller_one_pass_success(mock_gen, mock_val, mock_parse, mock_one):
    mock_one.return_value = OnePassResult("P", "R", "M", "LLM")
    mock_parse.return_value = MagicMock(template="T")
    mock_val.return_value = True

    controller = GenerationController("KEY", "M")
    controller.run("S")

    mock_one.assert_called()
    mock_gen.generate.assert_called()


@pytest.mark.skip(reason="Deferred: inspect this test later.")
@patch("textfsm_ai.generation.controller.generation_controller.two_pass")
@patch("textfsm_ai.generation.controller.generation_controller.one_pass")
@patch("textfsm_ai.generation.controller.generation_controller.parse_from_response")
@patch("textfsm_ai.generation.controller.generation_controller.validate_template")
@patch("textfsm_ai.generation.controller.generation_controller.generator")
def test_controller_two_pass_success(
    mock_gen, mock_val, mock_parse, mock_one, mock_two
):
    mock_one.return_value = OnePassResult("P", "R", "M", "LLM")
    mock_two.return_value = TwoPassResult("A", "B", "C", "D", "M", "LLM")

    # one-pass fails validation
    mock_parse.return_value = MagicMock(template="T")
    mock_val.side_effect = [False, True]

    controller = GenerationController("KEY", "M")
    controller.run("S")

    mock_two.assert_called()
    mock_gen.generate.assert_called()


@pytest.mark.skip(reason="Deferred: inspect this test later.")
@patch("textfsm_ai.generation.controller.generation_controller.fallback")
@patch("textfsm_ai.generation.controller.generation_controller.two_pass")
@patch("textfsm_ai.generation.controller.generation_controller.one_pass")
@patch("textfsm_ai.generation.controller.generation_controller.parse_from_response")
@patch("textfsm_ai.generation.controller.generation_controller.validate_template")
@patch("textfsm_ai.generation.controller.generation_controller.generator")
def test_controller_fallback(
    mock_gen, mock_val, mock_parse, mock_one, mock_two, mock_fb
):
    mock_one.return_value = OnePassResult("P", "R", "M", "LLM")
    mock_two.return_value = TwoPassResult("A", "B", "C", "D", "M", "LLM")
    mock_fb.return_value = MagicMock()

    # both fail validation
    mock_parse.return_value = MagicMock(template="T")
    mock_val.return_value = False

    controller = GenerationController("KEY", "M")
    controller.run("S")

    mock_fb.assert_called()
    mock_gen.generate.assert_called()
