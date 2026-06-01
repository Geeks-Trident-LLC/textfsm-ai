import os

from click.testing import CliRunner

from textfsm_ai.cli.config_group import config_group


def test_config_init(monkeypatch):
    runner = CliRunner()

    monkeypatch.setattr("click.prompt", lambda *a, **k: "test-value")

    with runner.isolated_filesystem():
        result = runner.invoke(config_group, ["init", "-o", "x.config"])
        assert result.exit_code == 0
        assert "Config written" in result.output
        assert os.path.exists("x.config")
