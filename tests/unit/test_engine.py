# tests/unit/test_engine.py

from unittest.mock import MagicMock, patch

from textfsm_ai.engine import generate_template
from textfsm_ai.generation.support.generator import GenerationResult


@patch("textfsm_ai.engine.Controller")
def test_generate_template_calls_controller(mock_controller_cls):
    api_key = "KEY123"
    model = "deepseek-chat"
    sample = "show version"

    # Mock controller instance + its run() result
    controller_instance = MagicMock()
    mock_controller_cls.return_value = controller_instance

    expected_result = GenerationResult(
        template="TEMPLATE",
        status="valid_raw",
        structured=MagicMock(),
    )
    controller_instance.run.return_value = expected_result

    # Run engine
    result = generate_template(api_key, model, sample)

    # Assertions
    mock_controller_cls.assert_called_once_with(api_key=api_key, model=model)
    controller_instance.run.assert_called_once_with(sample)

    assert result is expected_result
