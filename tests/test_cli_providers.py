from __future__ import annotations

import os
from click.testing import CliRunner
from textfsm_ai.cli.top import main


def test_providers_list_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["providers", "list"])
    assert result.exit_code == 0
    assert "openai" in result.output
    assert "anthropic" in result.output
    assert "gemini" in result.output
    assert "azure" in result.output


def test_providers_info_no_config(monkeypatch):
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
    runner = CliRunner()
    result = runner.invoke(
        main, ["orchestrator", "route", "--model", "openai/gpt-4o-mini"]
    )
    assert result.exit_code == 0
    assert "Routed provider" in result.output
    assert "openai" in result.output
