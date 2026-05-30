from click.testing import CliRunner
from textfsm_ai.cli.top import cli
import json


def test_json_output_structure():
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "providers"])

    assert result.exit_code == 0

    data = json.loads(result.output)
    assert "output" in data
    assert "elapsed_sec" in data
    assert isinstance(data["elapsed_sec"], float)
    assert "openai" in data["output"]  # human output captured
