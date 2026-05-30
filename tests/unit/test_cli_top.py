from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "textfsm-ai" in result.output.lower()
    assert "generate" in result.output
    assert "providers" in result.output
    assert "quota" in result.output
