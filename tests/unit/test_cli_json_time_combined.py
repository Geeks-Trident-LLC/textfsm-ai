import json

from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_json_and_time_together():
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "--time", "providers"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert "output" in data
    assert "elapsed_sec" in data
    assert isinstance(data["elapsed_sec"], float)

    # --time should NOT add human-readable timing in JSON mode
    assert "[time]" not in data["output"]
