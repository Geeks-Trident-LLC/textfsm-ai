import textfsm_ai.config_loader as loader


def test_load_config():
    cfg = loader.load_config()
    assert "providers" in cfg
    assert "openai" in cfg["providers"]
    assert "model" in cfg["providers"]["openai"]
