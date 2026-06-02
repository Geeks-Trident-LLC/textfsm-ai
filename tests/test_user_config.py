import tempfile
from pathlib import Path

from textfsm_ai.user_config import UserConfig, load_user_config, save_user_config


def test_user_config_roundtrip():
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / "cfg.json"

    cfg = UserConfig("openai", "gpt-5.5", "abc")
    save_user_config(path, cfg)

    loaded = load_user_config(path)
    assert loaded.provider == "openai"
    assert loaded.model == "gpt-5.5"
    assert loaded.api_key == "abc"
