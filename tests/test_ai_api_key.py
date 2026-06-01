import os

import pytest
import requests


def _should_run_live():
    return os.getenv("RUN_LIVE_TESTS") == "1"


def _assert_ok(resp, provider):
    assert (
        resp.status_code == 200
    ), f"{provider} returned {resp.status_code}: {resp.text}"


@pytest.mark.live
@pytest.mark.skipif(not _should_run_live(), reason="RUN_LIVE_TESTS=1 not set")
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY missing")
def test_openai_key_valid():
    key = os.getenv("OPENAI_API_KEY")

    # Fastest endpoint: list models (no generation)
    resp = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10,
    )

    _assert_ok(resp, "OpenAI")


@pytest.mark.live
@pytest.mark.skipif(not _should_run_live(), reason="RUN_LIVE_TESTS=1 not set")
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY missing"
)
def test_anthropic_key_valid():
    key = os.getenv("ANTHROPIC_API_KEY")

    # Fastest endpoint: list models
    resp = requests.get(
        "https://api.anthropic.com/v1/models",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        timeout=10,
    )

    _assert_ok(resp, "Anthropic")


@pytest.mark.live
@pytest.mark.skipif(not _should_run_live(), reason="RUN_LIVE_TESTS=1 not set")
@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY missing")
def test_gemini_key_valid():
    key = os.getenv("GEMINI_API_KEY")

    # Fastest endpoint: list models
    resp = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": key},
        timeout=10,
    )

    _assert_ok(resp, "Gemini")


@pytest.mark.live
@pytest.mark.skipif(not _should_run_live(), reason="RUN_LIVE_TESTS=1 not set")
@pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"), reason="DEEPSEEK_API_KEY missing"
)
def test_deepseek_key_valid():
    key = os.getenv("DEEPSEEK_API_KEY")

    # Fastest endpoint: list models
    resp = requests.get(
        "https://api.deepseek.com/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10,
    )

    _assert_ok(resp, "DeepSeek")
