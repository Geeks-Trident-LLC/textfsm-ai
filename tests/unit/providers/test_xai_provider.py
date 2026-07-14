from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from textfsm_ai.providers.xai_provider import XAIProvider


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="XAI_API_KEY"):
        XAIProvider(api_key=None, default_model="grok-3-mini")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "sk-from-env")
    p = XAIProvider(default_model="grok-3-mini")
    assert p.default_model == "grok-3-mini"
    assert p.name == "xai"


def test_init_sets_xai_base_url():
    p = XAIProvider(api_key="sk-test", default_model="grok-3-mini")
    assert "x.ai" in str(p.sync_client.base_url)


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="XAI_API_KEY"):
        XAIProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "sk-from-env")
    p = XAIProvider.from_env()
    assert isinstance(p, XAIProvider)


def test_fetch_latest_models():
    p = XAIProvider(api_key="sk-test", default_model="grok-3-mini")
    fake_models = [
        SimpleNamespace(id="grok-4"),
        SimpleNamespace(id="grok-3-mini"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["grok-4", "grok-3-mini"]
