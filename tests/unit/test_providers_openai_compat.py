# tests/unit/test_providers_openai_compat.py

from __future__ import annotations

import pytest

from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider


@pytest.mark.asyncio
async def test_openai_compat_provider_basic():
    """
    Basic smoke test: provider can be constructed with the new signature.
    We don't hit the real API here.
    """
    provider = OpenAICompatProvider(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        default_model="deepseek-chat",
    )

    assert isinstance(provider, OpenAICompatProvider)
