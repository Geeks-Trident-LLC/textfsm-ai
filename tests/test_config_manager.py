import tempfile

from textfsm_ai.config_manager import ProviderConfig, load_named_config, save_config


def test_save_and_load_named_config(monkeypatch):
    tmp = tempfile.TemporaryDirectory()
    monkeypatch.setenv("HOME", tmp.name)

    cfg = ProviderConfig("deepseek", "deepseek-chat", "abc")
    path = save_config("deepseek", cfg)

    assert path.exists()

    loaded = load_named_config("deepseek")
    assert loaded.provider == "deepseek"
    assert loaded.model == "deepseek-chat"
    assert loaded.api_key == "abc"
