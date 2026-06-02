import pytest

from textfsm_ai.model_selector import (
    get_model,
    is_chat_model,
    select_model_by_tier,
)

# -------------------------
# Chat model regex tests
# -------------------------


@pytest.mark.parametrize(
    "name",
    [
        "gpt-5.5",
        "gpt-5.4-mini",
        "gpt-5.4-nano",
        "gpt-5.2-pro",
        "gpt-5.2-thinking",
        "gpt-5.2-instant",
    ],
)
def test_openai_chat(name):
    assert is_chat_model("openai", name)


@pytest.mark.parametrize(
    "name",
    [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ],
)
def test_gemini_chat(name):
    assert is_chat_model("gemini", name)


@pytest.mark.parametrize(
    "name",
    [
        "claude-opus-4-8",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    ],
)
def test_anthropic_chat(name):
    assert is_chat_model("anthropic", name)


@pytest.mark.parametrize(
    "name",
    [
        "deepseek-v4-flash",
        "deepseek-v4-pro",
    ],
)
def test_deepseek_chat(name):
    assert is_chat_model("deepseek", name)


# -------------------------
# Tier selection tests
# -------------------------


def test_openai_tier_quality():
    models = ["gpt-5.5", "gpt-5.4-mini", "gpt-5.4-pro"]
    assert select_model_by_tier("openai", models, "quality") == "gpt-5.5"


def test_openai_tier_quality_reasoning():
    models = ["gpt-5.5", "gpt-5.4-pro", "gpt-5.3-pro"]
    assert select_model_by_tier("openai", models, "quality-reasoning") == "gpt-5.4-pro"


def test_gemini_tier_fast():
    models = ["gemini-2.5-pro", "gemini-2.5-flash-lite"]
    assert select_model_by_tier("gemini", models, "fast") == "gemini-2.5-flash-lite"


def test_anthropic_tier_balance():
    models = ["claude-opus-4-8", "claude-sonnet-4-6"]
    assert select_model_by_tier("anthropic", models, "balance") == "claude-sonnet-4-6"


def test_deepseek_tier_quality():
    models = ["deepseek-v4-flash", "deepseek-v4-pro"]
    assert select_model_by_tier("deepseek", models, "quality") == "deepseek-v4-pro"


# -------------------------
# get_model() tests
# -------------------------


def test_get_model(monkeypatch):
    def fake_list(provider, key):
        return ["gpt-5.5", "gpt-5.4-mini", "gpt-5.4-pro"]

    monkeypatch.setattr("textfsm_ai.model_selector.list_models", fake_list)

    out = get_model("openai", "dummy", "quality")
    assert out == "gpt-5.5"
