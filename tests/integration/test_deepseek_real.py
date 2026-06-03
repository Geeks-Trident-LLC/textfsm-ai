import os

import pytest

from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deepseek_real_basic():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        pytest.skip("Requires DEEPSEEK_API_KEY")

    if os.environ.get("TEST_REAL") != "true":
        pytest.skip("Requires TEST_REAL=true")

    provider = OpenAICompatProvider(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
    )

    result = await provider.generate("Say hello in one short sentence.")

    # Basic sanity checks
    assert isinstance(result.content, str)
    assert len(result.content.strip()) > 0

    # Provider metadata
    assert result.provider == "openai_compat"
    assert result.model == "deepseek-chat"

    # Raw response should contain choices
    assert isinstance(result.raw, dict)
    assert "choices" in result.raw
