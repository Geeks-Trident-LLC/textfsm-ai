from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider


def _fake_response(
    content="hello", prompt_tokens=5, completion_tokens=15, total_tokens=20
):
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice], usage=usage)


def _make_provider():
    return OpenAICompatProvider(
        api_key="sk-test",
        base_url="https://api.example.com",
        default_model="model-x",
    )


def test_supports_always_true():
    p = _make_provider()
    assert p.supports("anything-at-all")


@pytest.mark.asyncio
async def test_generate_success():
    p = _make_provider()
    p.client.chat.completions.create = AsyncMock(return_value=_fake_response())

    result = await p.generate(prompt="hi", model="model-x")

    assert result["content"] == "hello"
    assert result["usage"]["prompt_tokens"] == 5
    assert result["usage"]["total_tokens"] == 20


@pytest.mark.asyncio
async def test_generate_wraps_exceptions_in_provider_error():
    p = _make_provider()
    p.client.chat.completions.create = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        await p.generate(prompt="hi", model="model-x")


def test_generate_sync_success():
    p = _make_provider()
    p.sync_client.chat.completions.create = MagicMock(return_value=_fake_response())

    result = p.generate_sync(prompt="hi", model="model-x")

    assert result["content"] == "hello"
    assert result["usage"]["completion_tokens"] == 15


def test_generate_sync_wraps_exceptions_in_provider_error():
    p = _make_provider()
    p.sync_client.chat.completions.create = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(ProviderError):
        p.generate_sync(prompt="hi", model="model-x")
