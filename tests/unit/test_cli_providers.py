from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_providers_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["providers"])
    assert result.exit_code == 0
    assert "openai" in result.output
