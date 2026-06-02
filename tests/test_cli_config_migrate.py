import tempfile

from click.testing import CliRunner

from textfsm_ai.cli.config_migrate_cmd import config_migrate


def test_config_migrate(monkeypatch):
    tmp = tempfile.TemporaryDirectory()
    monkeypatch.setenv("HOME", tmp.name)
    monkeypatch.setenv("OPENAI_API_KEY", "abc")

    def fake_get(provider, key, tier):
        return "gpt-5.5"

    monkeypatch.setattr("textfsm_ai.cli.config_migrate_cmd.get_model", fake_get)

    runner = CliRunner()
    result = runner.invoke(config_migrate, ["--tier", "quality"])

    assert result.exit_code == 0
    assert "gpt-5.5" in result.output
