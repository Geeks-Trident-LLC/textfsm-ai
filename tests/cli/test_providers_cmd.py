from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from textfsm_ai.cli.providers_cmd import providers_test
from textfsm_ai.orchestrator.types import OrchestratorResponse


def test_providers_test_cli():
    runner = CliRunner()

    # Fake orchestrator response
    fake_resp = OrchestratorResponse(
        provider="openai", model="openai/gpt-4o-mini", raw={"content": "hello world"}
    )

    func_name = "textfsm_ai.cli.providers_cmd.create_orchestrator_from_config"

    # Patch config loader + orchestrator factory + asyncio.run
    with (
        patch("textfsm_ai.cli.providers_cmd._load_config") as mock_load_cfg,
        patch(func_name) as mock_factory,
        patch("textfsm_ai.cli.providers_cmd.asyncio.run") as mock_async_run,
    ):
        mock_load_cfg.return_value = MagicMock()  # config object not used
        mock_orch = MagicMock()
        mock_factory.return_value = mock_orch

        # When asyncio.run(orch.run(req)) is called, return fake_resp
        mock_async_run.return_value = fake_resp

        result = runner.invoke(
            providers_test, ["--model", "openai/gpt-4o-mini", "--prompt", "hello"]
        )

    # Assertions
    assert result.exit_code == 0
    output = result.output

    assert "Provider: openai" in output
    assert "Model: openai/gpt-4o-mini" in output
    assert "hello world" in output

    # Ensure orchestrator was actually called
    mock_async_run.assert_called_once()
    mock_factory.assert_called_once()
