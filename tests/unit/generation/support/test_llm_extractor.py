# tests/unit/generation/support/test_llm_extractor.py

from unittest.mock import patch

import anyask

from textfsm_ai.generation.core.models import LLMRawResponse
from textfsm_ai.generation.support.llm_extractor import extract


def _ask_response(content="hello", prompt_tokens=10, completion_tokens=20, raw="RAW"):
    return anyask.AskResponse(
        content=content,
        usage=anyask.TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        finish_reason="stop",
        provider="anthropic",
        model="x",
        raw=raw,
    )


def test_extract_success_nonempty():
    with patch("anyask.ask", return_value=_ask_response(content="hello")):
        result = extract("anthropic", model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is True
    assert result.raw["content"] == "hello"
    assert result.raw["usage"] == {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
    }
    assert result.raw["raw"] == "RAW"
    assert result.reason == ""


def test_extract_empty_content():
    with patch("anyask.ask", return_value=_ask_response(content="")):
        result = extract("anthropic", model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.reason == "provider returned response without content"


def test_extract_none_content():
    with patch("anyask.ask", return_value=_ask_response(content=None)):
        result = extract("anthropic", model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.reason == "provider returned response without content"


def test_extract_provider_error_exception():
    with patch("anyask.ask", side_effect=anyask.ProviderError("boom")):
        result = extract("anthropic", model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.raw == {}
    assert "ProviderError" in result.reason
    assert "boom" in result.reason


def test_extract_provider_auth_error_exception():
    with patch("anyask.ask", side_effect=anyask.ProviderAuthError("no api key")):
        result = extract("anthropic", model="x", prompt="test")

    assert result.ready is False
    assert "ProviderAuthError" in result.reason
    assert "no api key" in result.reason


def test_extract_provider_not_found_exception():
    with patch("anyask.ask", side_effect=anyask.ProviderNotFoundError("unknown")):
        result = extract("bogus", model="x", prompt="test")

    assert result.ready is False
    assert "ProviderNotFoundError" in result.reason


def test_extract_generic_exception():
    with patch("anyask.ask", side_effect=RuntimeError("network down")):
        result = extract("anthropic", model="x", prompt="test")

    assert result.ready is False
    assert "RuntimeError" in result.reason
    assert "network down" in result.reason


def test_extract_forwards_provider_model_prompt_and_kwargs():
    with patch("anyask.ask", return_value=_ask_response()) as mock_ask:
        extract(
            "azure",
            model="my-deployment",
            prompt="test prompt",
            api_key="k",
            endpoint="https://example.azure.com",
        )

    mock_ask.assert_called_once_with(
        "test prompt",
        provider="azure",
        model="my-deployment",
        api_key="k",
        endpoint="https://example.azure.com",
    )
