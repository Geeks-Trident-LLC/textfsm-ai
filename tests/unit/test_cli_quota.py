from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_quota_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["quota"])
    assert result.exit_code == 0
    assert "[quota]" in result.output
