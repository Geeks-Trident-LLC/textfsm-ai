import tempfile
from pathlib import Path

from click.testing import CliRunner

from textfsm_ai.cli.config_init_cmd import config_init


def test_config_init_creates_file():
    tmp = tempfile.TemporaryDirectory()
    cfg = Path(tmp.name) / "openai.config"

    runner = CliRunner()

    # Simulate user input for the three prompts
    user_input = "openai\ngpt-5.5\nabc123\n"

    result = runner.invoke(
        config_init,
        ["--output", str(cfg)],
        input=user_input,
    )
    assert result.exit_code == 1
    assert "Failed to list models" in result.output
