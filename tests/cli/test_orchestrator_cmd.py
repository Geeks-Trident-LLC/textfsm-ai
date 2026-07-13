# tests/cli/test_orchestrator_cmd.py

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from textfsm_ai.cli.orchestrator_cmd import _load_config
from textfsm_ai.cli.top import main
from textfsm_ai.orchestrator.types import OrchestratorResponse
from textfsm_ai.providers.config import OrchestratorConfig


# ---------------------------------------------------------
# _load_config
# ---------------------------------------------------------
def test_load_config_uses_env_when_no_path():
    sentinel = OrchestratorConfig(providers={})

    with patch(
        "textfsm_ai.cli.orchestrator_cmd.load_config_from_env", return_value=sentinel
    ) as mock_env:
        result = _load_config(None)

    mock_env.assert_called_once_with()
    assert result is sentinel


def test_load_config_uses_file_when_path_given():
    sentinel = OrchestratorConfig(providers={})

    with patch(
        "textfsm_ai.cli.orchestrator_cmd.load_config_from_file", return_value=sentinel
    ) as mock_file:
        result = _load_config("some/config.yaml")

    mock_file.assert_called_once_with("some/config.yaml")
    assert result is sentinel


# ---------------------------------------------------------
# orchestrator run
# ---------------------------------------------------------
class _FakeOrchestrator:
    def __init__(self, response):
        self._response = response

    async def run(self, req):
        return self._response


def test_orchestrator_run_uses_env_config():
    response = OrchestratorResponse(
        provider="gemini", model="gemini-2.5-flash", raw={"content": "hello there"}
    )

    with (
        patch(
            "textfsm_ai.cli.orchestrator_cmd.load_config_from_env",
            return_value=OrchestratorConfig(providers={}),
        ),
        patch(
            "textfsm_ai.cli.orchestrator_cmd.create_orchestrator_from_config",
            return_value=_FakeOrchestrator(response),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["orchestrator", "run", "--model", "gemini-2.5-flash", "--prompt", "hi"],
        )

    assert result.exit_code == 0
    assert "Provider: gemini" in result.output
    assert "Model: gemini-2.5-flash" in result.output
    assert "hello there" in result.output


def test_orchestrator_run_uses_config_path(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("providers: []\n")

    response = OrchestratorResponse(
        provider="openai", model="gpt-4o-mini", raw={"content": "ok"}
    )

    with (
        patch(
            "textfsm_ai.cli.orchestrator_cmd.load_config_from_file",
            return_value=OrchestratorConfig(providers={}),
        ) as mock_file,
        patch(
            "textfsm_ai.cli.orchestrator_cmd.create_orchestrator_from_config",
            return_value=_FakeOrchestrator(response),
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "orchestrator",
                "run",
                "--config",
                str(config_file),
                "--model",
                "gpt-4o-mini",
                "--prompt",
                "hi",
            ],
        )

    mock_file.assert_called_once_with(str(config_file))
    assert result.exit_code == 0
    assert "Provider: openai" in result.output
