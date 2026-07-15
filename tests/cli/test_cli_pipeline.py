# tests/cli/test_cli_pipeline.py

from __future__ import annotations

from unittest.mock import Mock, patch

from click.testing import CliRunner

from textfsm_ai.cli.top import main
from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.core.package import DeliveryOutput


def _write_input(tmp_path, text="hostname Router1\n"):
    input_file = tmp_path / "input.txt"
    input_file.write_text(text, encoding="utf-8")
    return str(input_file)


def test_pipeline_unknown_provider_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    input_file = _write_input(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        main, ["pipeline", input_file, "--provider", "not-a-real-provider"]
    )

    assert result.exit_code != 0
    assert "Unknown provider" in result.output


@patch("textfsm_ai.cli.pipeline_cmd.DeliveryController")
def test_pipeline_success_prints_output(mock_controller_cls, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    input_file = _write_input(tmp_path)

    mock_controller = Mock()
    mock_controller.run.return_value = DeliveryOutput(
        mode=DeliveryMode.DEFAULT,
        output="=== Output ===\nValue hostname (\\S+)",
        passed=True,
        error="",
    )
    mock_controller_cls.return_value = mock_controller

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["pipeline", input_file, "--provider", "openai", "--model", "gpt-4o-mini"],
    )

    assert result.exit_code == 0
    assert "Value hostname" in result.output

    mock_controller_cls.assert_called_once()
    _, kwargs = mock_controller_cls.call_args
    assert kwargs["provider_name"] == "openai"
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["api_key"] == "sk-test"

    mock_controller.run.assert_called_once()
    run_args, run_kwargs = mock_controller.run.call_args
    assert run_args[0] == "hostname Router1\n"
    assert run_kwargs["mode"] == "default"
    assert run_kwargs["as_json"] is False


@patch("textfsm_ai.cli.pipeline_cmd.DeliveryController")
def test_pipeline_failure_sets_nonzero_exit(mock_controller_cls, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    input_file = _write_input(tmp_path)

    mock_controller = Mock()
    mock_controller.run.return_value = DeliveryOutput(
        mode=DeliveryMode.DEFAULT,
        output="=== FAIL: build-ast ===\nBUILD-AST-ERROR",
        passed=False,
        error="BUILD-AST-ERROR",
    )
    mock_controller_cls.return_value = mock_controller

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["pipeline", input_file, "--provider", "openai", "--model", "gpt-4o-mini"],
    )

    assert result.exit_code != 0
    assert "FAIL" in result.output


@patch("textfsm_ai.cli.pipeline_cmd.DeliveryController")
def test_pipeline_mode_and_json_flags_passed_through(
    mock_controller_cls, tmp_path, monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    input_file = _write_input(tmp_path)

    mock_controller = Mock()
    mock_controller.run.return_value = DeliveryOutput(
        mode=DeliveryMode.DEBUG,
        output="{}",
        passed=True,
        error="",
    )
    mock_controller_cls.return_value = mock_controller

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "pipeline",
            input_file,
            "--provider",
            "openai",
            "--model",
            "gpt-4o-mini",
            "--mode",
            "debug",
            "--json",
        ],
    )

    assert result.exit_code == 0

    _, run_kwargs = mock_controller.run.call_args
    assert run_kwargs["mode"] == "debug"
    assert run_kwargs["as_json"] is True


def test_pipeline_invalid_mode_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    input_file = _write_input(tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "pipeline",
            input_file,
            "--provider",
            "openai",
            "--model",
            "gpt-4o-mini",
            "--mode",
            "not-a-real-mode",
        ],
    )

    assert result.exit_code != 0


def test_pipeline_missing_input_file():
    runner = CliRunner()
    result = runner.invoke(
        main, ["pipeline", "does-not-exist.txt", "--provider", "openai"]
    )

    assert result.exit_code != 0
