from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate


def test_generate_basic_output(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    with patch(
        "textfsm_ai.cli.generate_cmd.ask_ai", new_callable=AsyncMock
    ) as mock_ask:
        resp = mock_ask.return_value
        resp.content = "mocked output"
        resp.to_json.return_value = json.dumps({"output": "mocked output"})

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
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    with patch(
        "textfsm_ai.cli.generate_cmd.ask_ai", new_callable=AsyncMock
    ) as mock_ask:
        resp = mock_ask.return_value
        resp.content = "mocked output"
        resp.to_json = lambda: json.dumps({"output": "mocked output"})

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

    parsed = json.loads(result.output)
    assert parsed["output"] == "mocked output"


def test_generate_requires_model(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(generate, [str(input_file)])

    assert result.exit_code != 0
    assert "Missing option '--model'" in result.output
