from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_time_human_mode():
    runner = CliRunner()
    result = runner.invoke(cli, ["--time", "providers"])

    assert result.exit_code == 0
    assert "[time]" in result.output.lower()
