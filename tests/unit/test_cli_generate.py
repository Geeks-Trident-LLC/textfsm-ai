import pathlib
from click.testing import CliRunner

from textfsm_ai.cli.top import cli


def test_generate_requires_file(tmp_path: pathlib.Path):
    input_file = tmp_path / "sample.txt"
    input_file.write_text("show version\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["generate", str(input_file)])
    assert result.exit_code == 0
    assert "template from:" in result.output
    assert "Provider:" in result.output
