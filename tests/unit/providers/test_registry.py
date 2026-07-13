import pytest

from textfsm_ai.providers.anthropic_provider import AnthropicProvider
from textfsm_ai.providers.groq_provider import GroqProvider
from textfsm_ai.providers.openai_provider import OpenAIProvider
from textfsm_ai.providers.registry import (
    ProviderRegistry,
    get_provider_by_name,
    registry,
)
from textfsm_ai.providers.together_provider import TogetherProvider
from textfsm_ai.providers.xai_provider import XAIProvider


def test_registry_get_returns_registered_class():
    assert registry.get("openai") is OpenAIProvider
    assert registry.get("anthropic") is AnthropicProvider
    assert registry.get("groq") is GroqProvider
    assert registry.get("xai") is XAIProvider
    assert registry.get("together") is TogetherProvider


def test_registry_get_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        registry.get("not-a-real-provider")


def test_registry_all_returns_copy_not_internal_dict():
    all_providers = registry.all()
    assert "openai" in all_providers

    all_providers["fake"] = object()
    assert "fake" not in registry.all()


def test_registry_register_adds_new_entry():
    class _FakeProvider:
        name = "fake-provider"

    r = ProviderRegistry()
    r.register(_FakeProvider)
    assert r.get("fake-provider") is _FakeProvider


def test_get_provider_by_name_success():
    assert get_provider_by_name("openai") is OpenAIProvider


def test_get_provider_by_name_lowercases_input():
    assert get_provider_by_name("OpenAI") is OpenAIProvider
    assert get_provider_by_name("ANTHROPIC") is AnthropicProvider


def test_get_provider_by_name_unknown_raises_valueerror():
    with pytest.raises(ValueError, match="Unknown provider name"):
        get_provider_by_name("not-a-real-provider")
