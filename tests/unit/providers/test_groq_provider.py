from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from textfsm_ai.providers.groq_provider import GroqProvider


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        GroqProvider(api_key=None, default_model="llama-3.1-8b-instant")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "sk-from-env")
    p = GroqProvider(default_model="llama-3.1-8b-instant")
    assert p.default_model == "llama-3.1-8b-instant"
    assert p.name == "groq"


def test_init_sets_groq_base_url():
    p = GroqProvider(api_key="sk-test", default_model="llama-3.1-8b-instant")
    assert "groq.com" in str(p.sync_client.base_url)


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        GroqProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "sk-from-env")
    p = GroqProvider.from_env()
    assert isinstance(p, GroqProvider)


def test_fetch_latest_models():
    p = GroqProvider(api_key="sk-test", default_model="llama-3.1-8b-instant")
    fake_models = [
        SimpleNamespace(id="llama-3.3-70b-versatile"),
        SimpleNamespace(id="llama-3.1-8b-instant"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
