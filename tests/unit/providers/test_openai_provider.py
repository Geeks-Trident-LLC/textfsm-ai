from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.providers.openai_provider import OpenAIProvider


def _fake_response(
    content="hello", prompt_tokens=10, completion_tokens=20, total_tokens=30
):
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice], usage=usage)


def test_init_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIProvider(api_key=None, default_model="gpt-4o-mini")


def test_init_uses_env_var_when_no_explicit_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    p = OpenAIProvider(default_model="gpt-4o-mini")
    assert p.default_model == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_generate_success():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    p.client.chat.completions.create = AsyncMock(return_value=_fake_response())

    result = await p.generate(prompt="hi", model="gpt-4o-mini")

    assert result["content"] == "hello"
    assert result["usage"]["prompt_tokens"] == 10
    assert result["usage"]["completion_tokens"] == 20
    assert result["usage"]["total_tokens"] == 30


@pytest.mark.asyncio
async def test_generate_wraps_exceptions_in_provider_error():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    p.client.chat.completions.create = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        await p.generate(prompt="hi", model="gpt-4o-mini")


def test_generate_sync_success():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    p.sync_client.chat.completions.create = MagicMock(return_value=_fake_response())

    result = p.generate_sync(prompt="hi", model="gpt-4o-mini")

    assert result["content"] == "hello"
    assert result["usage"]["total_tokens"] == 30


def test_generate_sync_wraps_exceptions_in_provider_error():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    p.sync_client.chat.completions.create = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        p.generate_sync(prompt="hi", model="gpt-4o-mini")


def test_from_env_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPEN_API_KEY"):
        OpenAIProvider.from_env()


def test_from_env_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    p = OpenAIProvider.from_env()
    assert isinstance(p, OpenAIProvider)


def test_fetch_latest_models():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    fake_models = [SimpleNamespace(id="gpt-4o"), SimpleNamespace(id="gpt-4o-mini")]
    p.sync_client.models.list = MagicMock(
        return_value=SimpleNamespace(data=fake_models)
    )

    names = p.fetch_latest_models()

    assert names == ["gpt-4o", "gpt-4o-mini"]


def test_supports_matches_gpt_and_o_series():
    p = OpenAIProvider(api_key="sk-test", default_model="gpt-4o-mini")
    assert p.supports("gpt-4o-mini")
    assert p.supports("o1-preview")
    assert not p.supports("claude-3-5-sonnet")
