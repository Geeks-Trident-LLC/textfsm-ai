from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_cli_version_subcommand():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "textfsm-ai" in result.output.lower()
