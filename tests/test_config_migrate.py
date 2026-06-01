from click.testing import CliRunner

from textfsm_ai.cli.config_migrate_cmd import config_migrate


def test_config_migrate(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "xyz")

    runner = CliRunner()
    result = runner.invoke(config_migrate)

    assert result.exit_code == 0
    assert "Migrated DEEPSEEK_API_KEY" in result.output
