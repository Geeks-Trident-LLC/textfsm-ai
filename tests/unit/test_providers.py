from __future__ import annotations

import pytest

from textfsm_ai.orchestrator.errors import ProviderError
from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider


@pytest.mark.parametrize(
    "provider_cls, model",
    [
        (OpenAIProvider, "openai/gpt-4o-mini"),
        (AnthropicProvider, "anthropic/claude-3-5-sonnet"),
        (GeminiProvider, "gemini/gemini-1.5-flash"),
    ],
)
def test_provider_supports_prefix(provider_cls, model):
    p = provider_cls(api_key="dummy")  # will fail on real call, but supports() is local
    assert p.supports(model)


def test_openai_provider_raises_on_failure(monkeypatch):
    p = OpenAIProvider(api_key="dummy")

    def fake_create(*args, **kwargs):
        raise RuntimeError("boom")

    p.client.chat.completions.create = fake_create  # type: ignore[attr-defined]

    with pytest.raises(ProviderError):
        p.generate(
            prompt="hi", model="openai/gpt-4o-mini", temperature=0.0, max_tokens=16
        )
