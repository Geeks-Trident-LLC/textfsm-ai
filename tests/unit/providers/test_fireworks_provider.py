from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from textfsm_ai.providers.fireworks_provider import FireworksProvider


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)
    with pytest.raises(ValueError, match="FIREWORKS_API_KEY"):
        FireworksProvider(
            api_key=None,
            default_model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        )


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("FIREWORKS_API_KEY", "sk-from-env")
    p = FireworksProvider(
        default_model="accounts/fireworks/models/llama-v3p1-8b-instruct"
    )
    assert p.default_model == "accounts/fireworks/models/llama-v3p1-8b-instruct"
    assert p.name == "fireworks"


def test_init_sets_fireworks_base_url():
    p = FireworksProvider(
        api_key="sk-test",
        default_model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    )
    assert "fireworks.ai" in str(p.sync_client.base_url)


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("FIREWORKS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FIREWORKS_API_KEY"):
        FireworksProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("FIREWORKS_API_KEY", "sk-from-env")
    p = FireworksProvider.from_env()
    assert isinstance(p, FireworksProvider)


def test_fetch_latest_models():
    p = FireworksProvider(
        api_key="sk-test",
        default_model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    )
    fake_models = [
        SimpleNamespace(id="accounts/fireworks/models/llama-v3p3-70b-instruct"),
        SimpleNamespace(id="accounts/fireworks/models/llama-v3p1-8b-instruct"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == [
        "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "accounts/fireworks/models/llama-v3p1-8b-instruct",
    ]
