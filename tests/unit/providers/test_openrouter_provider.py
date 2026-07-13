from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from textfsm_ai.providers.openrouter_provider import OpenRouterProvider


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider(api_key=None, default_model="google/gemini-2.5-flash-lite")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-from-env")
    p = OpenRouterProvider(default_model="google/gemini-2.5-flash-lite")
    assert p.default_model == "google/gemini-2.5-flash-lite"
    assert p.name == "openrouter"


def test_init_sets_openrouter_base_url():
    p = OpenRouterProvider(
        api_key="sk-test", default_model="google/gemini-2.5-flash-lite"
    )
    assert "openrouter.ai" in str(p.sync_client.base_url)


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-from-env")
    p = OpenRouterProvider.from_env()
    assert isinstance(p, OpenRouterProvider)


def test_fetch_latest_models():
    p = OpenRouterProvider(
        api_key="sk-test", default_model="google/gemini-2.5-flash-lite"
    )
    fake_models = [
        SimpleNamespace(id="openai/gpt-4o"),
        SimpleNamespace(id="anthropic/claude-3.5-sonnet"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"]
