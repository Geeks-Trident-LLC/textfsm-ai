from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from textfsm_ai.providers.moonshot_provider import MoonshotProvider


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MOONSHOT_API_KEY"):
        MoonshotProvider(api_key=None, default_model="moonshot-v1-8k")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-from-env")
    p = MoonshotProvider(default_model="moonshot-v1-8k")
    assert p.default_model == "moonshot-v1-8k"
    assert p.name == "moonshot"


def test_init_sets_moonshot_base_url():
    p = MoonshotProvider(api_key="sk-test", default_model="moonshot-v1-8k")
    assert "moonshot.ai" in str(p.sync_client.base_url)


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="MOONSHOT_API_KEY"):
        MoonshotProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-from-env")
    p = MoonshotProvider.from_env()
    assert isinstance(p, MoonshotProvider)


def test_fetch_latest_models():
    p = MoonshotProvider(api_key="sk-test", default_model="moonshot-v1-8k")
    fake_models = [
        SimpleNamespace(id="kimi-k2-0711-preview"),
        SimpleNamespace(id="moonshot-v1-8k"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["kimi-k2-0711-preview", "moonshot-v1-8k"]
