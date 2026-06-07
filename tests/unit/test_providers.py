from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider


@pytest.mark.parametrize(
    "provider_cls, model, default_model",
    [
        (OpenAIProvider, "openai/gpt-4o-mini", "openai/gpt-4o-mini"),
        (
            AnthropicProvider,
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-3-5-sonnet",
        ),
        (GeminiProvider, "gemini/gemini-1.5-flash", "gemini/gemini-1.5-flash"),
    ],
)
def test_provider_supports_prefix(provider_cls, model, default_model):
    """
    supports() is synchronous and should not require real API calls.
    """
    p = provider_cls(api_key="dummy", default_model=default_model)
    assert p.supports(model)


@pytest.mark.asyncio
async def test_openai_provider_raises_on_failure(monkeypatch):
    """
    generate() is async and should wrap underlying client errors into ProviderError.
    """
    p = OpenAIProvider(api_key="dummy", default_model="openai/gpt-4o-mini")

    fake = AsyncMock(side_effect=RuntimeError("boom"))
    monkeypatch.setattr(
        p.client.chat.completions,
        "create",
        fake,
    )

    with pytest.raises(ProviderError):
        await p.generate(
            prompt="hi",
            model="openai/gpt-4o-mini",
        )
