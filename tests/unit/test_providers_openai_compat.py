import pytest
import respx
import httpx

from textfsm_ai.providers.openai_compat_provider import OpenAICompatProvider


@pytest.mark.asyncio
@respx.mock
async def test_openai_compat_provider_basic():
    provider = OpenAICompatProvider(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat"
    )

    # Match ANY /v1/chat/completions URL
    mock_route = respx.post(
        url__regex=r"https://api\.deepseek\.com/v1/chat/completions/?$"
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Hello from DeepSeek"},
                        "finish_reason": "stop",
                    }
                ]
            },
        )
    )

    result = await provider.run("Hello")

    assert mock_route.called
    assert result.content == "Hello from DeepSeek"
