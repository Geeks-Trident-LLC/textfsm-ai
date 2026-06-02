import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from textfsm_ai.cli.config_show_cmd import config_show


def test_config_show():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / "openai.config"
    path.write_text(
        json.dumps({"provider": "openai", "model": "gpt-5.5", "api_key": "x"})
    )

    runner = CliRunner()
    result = runner.invoke(config_show, [str(path)])

    assert result.exit_code == 0
    assert "gpt-5.5" in result.output
