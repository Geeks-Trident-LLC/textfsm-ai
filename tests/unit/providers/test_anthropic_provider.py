from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.providers.anthropic_provider import AnthropicProvider


def _fake_response(text="hello", input_tokens=10, output_tokens=20):
    usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens)
    block = SimpleNamespace(text=text)
    return SimpleNamespace(content=[block], usage=usage)


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider(api_key=None, default_model="claude-sonnet-4-5")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-from-env")
    p = AnthropicProvider(default_model="claude-sonnet-4-5")
    assert p.default_model == "claude-sonnet-4-5"


def test_supports_always_true():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    assert p.supports("anything")


@pytest.mark.asyncio
async def test_generate_success_applies_default_temperature_and_max_tokens():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    p.client.messages.create = AsyncMock(return_value=_fake_response())

    result = await p.generate(prompt="hi", model="claude-sonnet-4-5")

    assert result["content"] == "hello"
    assert result["usage"]["prompt_tokens"] == 10
    assert result["usage"]["completion_tokens"] == 20
    assert result["usage"]["total_tokens"] == 30

    _, kwargs = p.client.messages.create.call_args
    assert kwargs["temperature"] == 0.2
    assert kwargs["max_tokens"] == 2048


@pytest.mark.asyncio
async def test_generate_respects_explicit_temperature_and_max_tokens():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    p.client.messages.create = AsyncMock(return_value=_fake_response())

    await p.generate(
        prompt="hi", model="claude-sonnet-4-5", temperature=0.9, max_tokens=100
    )

    _, kwargs = p.client.messages.create.call_args
    assert kwargs["temperature"] == 0.9
    assert kwargs["max_tokens"] == 100


@pytest.mark.asyncio
async def test_generate_wraps_exceptions_in_provider_error():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    p.client.messages.create = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        await p.generate(prompt="hi", model="claude-sonnet-4-5")


def test_generate_sync_success():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    p.sync_client.messages.create = MagicMock(return_value=_fake_response())

    result = p.generate_sync(prompt="hi", model="claude-sonnet-4-5")

    assert result["content"] == "hello"
    assert result["usage"]["total_tokens"] == 30


def test_generate_sync_wraps_exceptions_in_provider_error():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    p.sync_client.messages.create = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        p.generate_sync(prompt="hi", model="claude-sonnet-4-5")


def test_generate_sync_usage_none_gives_none_total():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    response = SimpleNamespace(content=[SimpleNamespace(text="hi")], usage=None)
    p.sync_client.messages.create = MagicMock(return_value=response)

    result = p.generate_sync(prompt="hi", model="claude-sonnet-4-5")

    assert result["usage"]["prompt_tokens"] is None
    assert result["usage"]["total_tokens"] is None


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-from-env")
    p = AnthropicProvider.from_env()
    assert isinstance(p, AnthropicProvider)


def test_fetch_latest_models():
    p = AnthropicProvider(api_key="sk-test", default_model="claude-sonnet-4-5")
    fake_models = [
        SimpleNamespace(id="claude-opus-4-8"),
        SimpleNamespace(id="claude-sonnet-4-5"),
    ]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["claude-opus-4-8", "claude-sonnet-4-5"]
