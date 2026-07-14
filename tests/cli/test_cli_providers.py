# tests/cli/test_cli_providers.py

from __future__ import annotations

from click.testing import CliRunner

from textfsm_ai.cli.top import main


def test_providers_list_runs():
    """
    The providers list command should always succeed and list all
    registered provider types, regardless of configuration.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["providers", "list"])

    assert result.exit_code == 0
    assert "openai" in result.output
    assert "anthropic" in result.output
    assert "gemini" in result.output
    assert "azure" in result.output
    assert "groq" in result.output
    assert "xai" in result.output
    assert "together" in result.output
    assert "fireworks" in result.output
    assert "cerebras" in result.output
    assert "perplexity" in result.output
    assert "openrouter" in result.output
    assert "moonshot" in result.output
    assert "mistral" in result.output
    assert "bedrock" in result.output
    assert "cohere" in result.output
    assert "vertexai" in result.output


def test_providers_info_no_config(monkeypatch):
    """
    With no environment variables set, providers should not be configured.
    The CLI should report that the provider is not configured.
    """
    # Ensure no provider is auto-configured from env vars
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)

    runner = CliRunner()
    result = runner.invoke(main, ["providers", "info", "--name", "openai"])

    assert result.exit_code == 0
    assert "No configured provider" in result.output


def test_orchestrator_route_basic():
    """
    The orchestrator route command should resolve the provider based on
    model prefix rules and print the routed provider name.
    """
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["orchestrator", "route", "--model", "openai/gpt-4o-mini"],
    )

    assert result.exit_code == 0
    assert "Routed provider" in result.output
    assert "openai" in result.output
