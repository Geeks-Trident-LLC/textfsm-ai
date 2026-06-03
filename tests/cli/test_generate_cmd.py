from __future__ import annotations

import json
from unittest.mock import patch

from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate


def test_generate_basic_output(tmp_path):
    # Create a temporary input file
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    # Mock ask_ai() to avoid real provider calls
    with patch("textfsm_ai.cli.generate_cmd.ask_ai") as mock_ask:
        mock_ask.return_value.content = "mocked output"
        mock_ask.return_value.to_json.return_value = json.dumps(
            {"output": "mocked output"}
        )

        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                str(input_file),
                "--model",
                "openai/gpt-4o-mini",
            ],
        )

    assert result.exit_code == 0
    assert "mocked output" in result.output


def test_generate_json_output(tmp_path):
    # Create a temporary input file
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    with patch("textfsm_ai.cli.generate_cmd.ask_ai") as mock_ask:
        mock_ask.return_value.content = "mocked output"
        mock_ask.return_value.to_json.return_value = json.dumps(
            {"output": "mocked output"}
        )

        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                str(input_file),
                "--model",
                "openai/gpt-4o-mini",
                "--json",
            ],
        )

    assert result.exit_code == 0

    # Output should be valid JSON
    parsed = json.loads(result.output)
    assert parsed["output"] == "mocked output"


def test_generate_requires_model(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(generate, [str(input_file)])

    # Click should error because --model is required
    assert result.exit_code != 0
    assert "Missing option '--model'" in result.output
