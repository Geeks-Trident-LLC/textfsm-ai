# tests/cli/test_providers_cmd.py

from unittest.mock import patch

import anyask
from click.testing import CliRunner

from textfsm_ai.cli.providers_cmd import (
    _load_config,
    providers_info,
    providers_list,
    providers_test,
)
from textfsm_ai.providers.config import ProviderConfig, ProvidersConfig


def test_providers_test_cli():
    runner = CliRunner()

    fake_resp = anyask.AskResponse(
        content="hello world",
        usage=anyask.TokenUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        finish_reason="stop",
        provider="openai",
        model="gpt-4o-mini",
        raw={},
    )

    with (
        patch("textfsm_ai.cli.providers_cmd._load_config") as mock_load_cfg,
        patch("textfsm_ai.cli.providers_cmd.anyask.ask") as mock_ask,
    ):
        mock_load_cfg.return_value = ProvidersConfig(providers={})
        mock_ask.return_value = fake_resp

        result = runner.invoke(
            providers_test,
            [
                "--provider",
                "openai",
                "--model",
                "gpt-4o-mini",
                "--prompt",
                "hello",
            ],
        )

    assert result.exit_code == 0
    output = result.output

    assert "Provider: openai" in output
    assert "Model: gpt-4o-mini" in output
    assert "hello world" in output

    mock_ask.assert_called_once_with("hello", provider="openai", model="gpt-4o-mini")


def test_providers_test_cli_passes_configured_params():
    runner = CliRunner()

    fake_resp = anyask.AskResponse(
        content="hi",
        usage=anyask.TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        finish_reason="stop",
        provider="anthropic",
        model="m",
        raw={},
    )

    cfg = ProvidersConfig(
        providers={
            "anthropic": ProviderConfig(
                name="anthropic", type="anthropic", params={"api_key": "sk-test"}
            )
        }
    )

    with (
        patch("textfsm_ai.cli.providers_cmd._load_config", return_value=cfg),
        patch("textfsm_ai.cli.providers_cmd.anyask.ask") as mock_ask,
    ):
        mock_ask.return_value = fake_resp

        runner.invoke(
            providers_test,
            ["--provider", "anthropic", "--model", "m", "--prompt", "hi"],
        )

    mock_ask.assert_called_once_with(
        "hi", provider="anthropic", model="m", api_key="sk-test"
    )


# ---------------------------------------------------------
# _load_config
# ---------------------------------------------------------
def test_load_config_uses_env_when_no_path():
    sentinel = ProvidersConfig(providers={})

    with patch(
        "textfsm_ai.cli.providers_cmd.load_config_from_env", return_value=sentinel
    ) as mock_env:
        result = _load_config(None)

    mock_env.assert_called_once_with()
    assert result is sentinel


def test_load_config_uses_file_when_path_given():
    sentinel = ProvidersConfig(providers={})

    with patch(
        "textfsm_ai.cli.providers_cmd.load_config_from_file", return_value=sentinel
    ) as mock_file:
        result = _load_config("some/config.yaml")

    mock_file.assert_called_once_with("some/config.yaml")
    assert result is sentinel


# ---------------------------------------------------------
# providers list
# ---------------------------------------------------------
def test_providers_list_empty_registry():
    runner = CliRunner()

    with patch("textfsm_ai.cli.providers_cmd.registry") as mock_registry:
        mock_registry.all.return_value = {}
        result = runner.invoke(providers_list)

    assert result.exit_code == 0
    assert "No providers registered." in result.output


# ---------------------------------------------------------
# providers info: configured provider found
# ---------------------------------------------------------
def test_providers_info_found_masks_sensitive_params():
    runner = CliRunner()

    cfg = ProvidersConfig(
        providers={
            "openai": ProviderConfig(
                name="openai",
                type="openai",
                params={"api_key": "sk-secret", "model": "gpt-4o-mini"},
            )
        }
    )

    with patch("textfsm_ai.cli.providers_cmd._load_config", return_value=cfg):
        result = runner.invoke(providers_info, ["--name", "openai"])

    assert result.exit_code == 0
    assert "Name: openai" in result.output
    assert "Type: openai" in result.output
    assert "'api_key': '***'" in result.output
    assert "'model': 'gpt-4o-mini'" in result.output
