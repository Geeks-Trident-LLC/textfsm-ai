import tempfile

from textfsm_ai.config_loader import load_config


def test_load_config_valid():
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write('provider="deepseek"\nmodel="deepseek-chat"\napi_key="123"')
        f.flush()
        cfg = load_config(f.name)
        assert cfg.provider == "deepseek"
        assert cfg.model == "deepseek-chat"
        assert cfg.api_key == "123"
