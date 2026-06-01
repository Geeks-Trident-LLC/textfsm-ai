import os

import pytest
import requests


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY is not set"
)
def test_anthropic_key_valid():
    key = os.getenv("ANTHROPIC_API_KEY")

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    # Use the smallest, oldest model that all accounts support
    payload = {
        "model": "claude-haiku-4-5-20251001",  # fastest & cheapest current model
        "max_tokens": 20,
        "messages": [{"role": "user", "content": "ping"}],
    }

    resp = requests.post(url, headers=headers, json=payload)

    assert (
        resp.status_code == 200
    ), f"Anthropic API returned {resp.status_code}: {resp.text}"


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is not set")
def test_openai_key_valid():
    key = os.getenv("OPENAI_API_KEY")

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "ping"}],
        },
    )

    assert resp.status_code == 200, f"OpenAI returned {resp.status_code}: {resp.text}"


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY is not set")
def test_gemini_key_valid():
    key = os.getenv("GEMINI_API_KEY")

    resp = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": key},
        json={
            "contents": [{"parts": [{"text": "ping"}]}],
            "generationConfig": {"maxOutputTokens": 10},
        },
        timeout=15,
    )

    assert resp.status_code == 200, f"API returned {resp.status_code}: {resp.text}"


@pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"), reason="DEEPSEEK_API_KEY is not set"
)
def test_deepseek_key_valid():
    key = os.getenv("DEEPSEEK_API_KEY")

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "ping"}],
    }

    resp = requests.post(url, headers=headers, json=payload)

    assert (
        resp.status_code == 200
    ), f"DeepSeek API returned {resp.status_code}: {resp.text}"
