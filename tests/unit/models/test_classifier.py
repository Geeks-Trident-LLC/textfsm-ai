# tests/unit/models/test_classifier.py

from textfsm_ai.models.classifier import classify_models
from textfsm_ai.models.tiers import Tier


def test_openai_classification():
    raw = ["gpt-4.1", "gpt-4.1-mini", "gpt-4o-nano", "o1", "o1-mini"]
    groups = classify_models("openai", raw)

    assert "gpt-4.1" in groups[Tier.QUALITY_CHAT]
    assert "gpt-4.1-mini" in groups[Tier.BALANCE_CHAT]
    assert "gpt-4o-nano" in groups[Tier.SPEED_CHAT]
    assert "o1" in groups[Tier.THINKING_CHAT]
    assert "o1-mini" in groups[Tier.THINKING_CHAT]


def test_gemini_classification():
    raw = ["gemini-2.0-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
    groups = classify_models("gemini", raw)

    assert "gemini-2.0-pro" in groups[Tier.QUALITY_CHAT]
    assert "gemini-2.0-flash" in groups[Tier.BALANCE_CHAT]
    assert "gemini-2.0-flash-lite" in groups[Tier.SPEED_CHAT]


def test_anthropic_classification():
    raw = ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]
    groups = classify_models("anthropic", raw)

    assert "claude-opus-4-8" in groups[Tier.QUALITY_CHAT]
    assert "claude-sonnet-4-6" in groups[Tier.BALANCE_CHAT]
    assert "claude-haiku-4-5-20251001" in groups[Tier.SPEED_CHAT]


def test_deepseek_classification():
    raw = ["deepseek-v4-pro", "deepseek-v4-flash", "deepseek-r1"]
    groups = classify_models("deepseek", raw)

    assert "deepseek-v4-pro" in groups[Tier.QUALITY_CHAT]
    assert "deepseek-v4-flash" in groups[Tier.BALANCE_CHAT]
    assert "deepseek-r1" in groups[Tier.THINKING_CHAT]
