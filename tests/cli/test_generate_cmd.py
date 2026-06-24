# tests/cli/test_generate_cmd.py

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from textfsm_ai.cli.generate_cmd import generate
from textfsm_ai.providers.config import OrchestratorConfig, ProviderConfig


def test_generate_basic_output(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    fake_provider = ProviderConfig(
        name="openai",
        type="openai",
        params={"api_key": "dummy", "model": "gpt-4o-mini"},
    )

    with (
        patch("textfsm_ai.cli.generate_cmd.load_config_from_file") as mock_file,
        patch("textfsm_ai.cli.generate_cmd.load_config_from_env") as mock_env,
        patch("textfsm_ai.cli.generate_cmd.GenerationController") as mock_ctrl,
    ):
        mock_file.return_value = OrchestratorConfig(providers={"openai": fake_provider})
        mock_env.return_value = OrchestratorConfig(providers={})

        instance = mock_ctrl.return_value
        instance.run.return_value.last_stage.template = "mocked output"
        instance.run.return_value.ready = True

        runner = CliRunner()
        result = runner.invoke(
            generate,
            [
                str(input_file),
                "--provider",
                "openai",
                "--model",
                "gpt-4o-mini",
            ],
        )

    assert result.exit_code == 0
    assert "mocked output" in result.output


def test_generate_requires_provider(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello world", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(generate, [str(input_file)])

    assert result.exit_code != 0
    assert "Missing option '--provider'" in result.output
