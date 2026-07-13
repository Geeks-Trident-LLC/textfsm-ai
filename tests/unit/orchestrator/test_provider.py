# tests/unit/orchestrator/test_provider.py

from __future__ import annotations

import pytest

from textfsm_ai.orchestrator.provider import Provider


class _ConcreteProvider(Provider):
    """Minimal concrete subclass overriding every abstract method, so we
    can invoke Provider's own stub bodies directly (unbound) to verify
    they raise NotImplementedError if a subclass ever calls super()."""

    def __init__(self, name: str) -> None:
        self.name = name

    def supports(self, model: str) -> bool:
        return True

    async def generate(self, prompt: str, *, model: str, **kwargs) -> dict:
        return {"content": "ok"}

    def generate_sync(self, prompt: str, *, model: str, **kwargs) -> dict:
        return {"content": "ok"}


def test_supports_stub_raises_not_implemented():
    provider = _ConcreteProvider("test")
    with pytest.raises(NotImplementedError):
        Provider.supports(provider, "some-model")


@pytest.mark.asyncio
async def test_generate_stub_raises_not_implemented():
    provider = _ConcreteProvider("test")
    with pytest.raises(NotImplementedError):
        await Provider.generate(provider, "prompt", model="m")


def test_generate_sync_stub_raises_not_implemented():
    provider = _ConcreteProvider("test")
    with pytest.raises(NotImplementedError):
        Provider.generate_sync(provider, "prompt", model="m")


def test_from_env_stub_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        _ConcreteProvider.from_env()
