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


def test_groq_classification():
    raw = [
        "llama-3.3-70b-versatile",  # large -> quality
        "qwen-2.5-32b",  # mid -> balance
        "llama-3.1-8b-instant",  # small -> speed
        "gemma2-9b-it",  # small -> speed
        "mixtral-8x7b-32768",  # MoE -> quality
        "deepseek-r1-distill-llama-70b",  # reasoning -> thinking
        "some-unknown-model",  # no match -> other
    ]
    groups = classify_models("groq", raw)

    assert "llama-3.3-70b-versatile" in groups[Tier.QUALITY_CHAT]
    assert "mixtral-8x7b-32768" in groups[Tier.QUALITY_CHAT]
    assert "qwen-2.5-32b" in groups[Tier.BALANCE_CHAT]
    assert "llama-3.1-8b-instant" in groups[Tier.SPEED_CHAT]
    assert "gemma2-9b-it" in groups[Tier.SPEED_CHAT]
    assert "deepseek-r1-distill-llama-70b" in groups[Tier.THINKING_CHAT]
    assert "some-unknown-model" in groups[Tier.OTHER]


def test_xai_classification():
    raw = [
        "grok-4",  # no suffix -> quality
        "grok-3-fast",  # fast -> balance
        "grok-3-mini",  # mini -> speed
        "grok-2-vision-1212",  # vision -> other
        "some-unknown-model",  # no match -> other
    ]
    groups = classify_models("xai", raw)

    assert "grok-4" in groups[Tier.QUALITY_CHAT]
    assert "grok-3-fast" in groups[Tier.BALANCE_CHAT]
    assert "grok-3-mini" in groups[Tier.SPEED_CHAT]
    assert "grok-2-vision-1212" in groups[Tier.OTHER]
    assert "some-unknown-model" in groups[Tier.OTHER]


# ---------------------------------------------------------
# _normalize (via the "provider/model" prefix form)
# ---------------------------------------------------------
def test_normalize_strips_provider_prefix():
    groups = classify_models("openai", ["openai/gpt-4.1"])

    assert "gpt-4.1" in groups[Tier.QUALITY_CHAT]


# ---------------------------------------------------------
# OpenAI: no-match and unhandled-suffix fallbacks
# ---------------------------------------------------------
def test_openai_classification_no_match_falls_to_other():
    groups = classify_models("openai", ["text-davinci-003"])

    assert "text-davinci-003" in groups[Tier.OTHER]


def test_openai_classification_unhandled_suffix_falls_to_other():
    groups = classify_models("openai", ["gpt-4.1-thinking"])

    assert "gpt-4.1-thinking" in groups[Tier.OTHER]


# ---------------------------------------------------------
# Gemini: no-match and unhandled-kind fallbacks
# ---------------------------------------------------------
def test_gemini_classification_no_match_falls_to_other():
    groups = classify_models("gemini", ["text-bison-001"])

    assert "text-bison-001" in groups[Tier.OTHER]


def test_gemini_classification_unhandled_kind_falls_to_other():
    groups = classify_models("gemini", ["gemini-2.0-flash-image"])

    assert "gemini-2.0-flash-image" in groups[Tier.OTHER]


# ---------------------------------------------------------
# Anthropic: no-match fallback
# ---------------------------------------------------------
def test_anthropic_classification_no_match_falls_to_other():
    groups = classify_models("anthropic", ["claude-instant-1"])

    assert "claude-instant-1" in groups[Tier.OTHER]


# ---------------------------------------------------------
# DeepSeek: native "chat" branch and full no-match fallback
# ---------------------------------------------------------
def test_deepseek_classification_native_chat():
    groups = classify_models("deepseek", ["deepseek-chat"])

    assert "deepseek-chat" in groups[Tier.BALANCE_CHAT]


def test_deepseek_classification_no_match_falls_to_other():
    groups = classify_models("deepseek", ["deepseek-v3"])

    assert "deepseek-v3" in groups[Tier.OTHER]


# ---------------------------------------------------------
# Unified classify_models(): azure alias and unknown provider
# ---------------------------------------------------------
def test_classify_models_azure_uses_openai_classifier():
    groups = classify_models("azure", ["gpt-4.1"])

    assert "gpt-4.1" in groups[Tier.QUALITY_CHAT]


def test_classify_models_unknown_provider_falls_to_other():
    groups = classify_models("mistral", ["mistral-large", "provider/mistral-small"])

    assert "mistral-large" in groups[Tier.OTHER]
    assert "mistral-small" in groups[Tier.OTHER]
