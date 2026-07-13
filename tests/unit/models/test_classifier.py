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


def test_together_classification():
    raw = [
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",  # 70B -> quality
        "mistralai/Mixtral-8x7B-Instruct-v0.1",  # MoE -> quality
        "Qwen/Qwen2.5-32B-Instruct",  # 32B -> balance
        "meta-llama/Llama-3.1-8B-Instruct-Turbo",  # 8B -> speed
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",  # reasoning -> thinking
        "deepseek-ai/DeepSeek-V3",  # no size token -> other
    ]
    groups = classify_models("together", raw)

    assert "meta-llama/Llama-3.3-70B-Instruct-Turbo" in groups[Tier.QUALITY_CHAT]
    assert "mistralai/Mixtral-8x7B-Instruct-v0.1" in groups[Tier.QUALITY_CHAT]
    assert "Qwen/Qwen2.5-32B-Instruct" in groups[Tier.BALANCE_CHAT]
    assert "meta-llama/Llama-3.1-8B-Instruct-Turbo" in groups[Tier.SPEED_CHAT]
    assert "deepseek-ai/DeepSeek-R1-Distill-Llama-70B" in groups[Tier.THINKING_CHAT]
    assert "deepseek-ai/DeepSeek-V3" in groups[Tier.OTHER]


def test_together_classification_preserves_vendor_prefix():
    # Unlike other providers, Together's classifier must NOT strip the
    # "vendor/" prefix - it's required to actually call the model.
    groups = classify_models("together", ["meta-llama/Llama-3.1-8B-Instruct-Turbo"])

    assert "meta-llama/Llama-3.1-8B-Instruct-Turbo" in groups[Tier.SPEED_CHAT]
    assert "Llama-3.1-8B-Instruct-Turbo" not in groups[Tier.SPEED_CHAT]


def test_fireworks_classification():
    raw = [
        "accounts/fireworks/models/llama-v3p3-70b-instruct",  # 70B -> quality
        "accounts/fireworks/models/mixtral-8x22b-instruct",  # MoE -> quality
        "accounts/fireworks/models/qwen2p5-32b-instruct",  # 32B -> balance
        "accounts/fireworks/models/llama-v3p1-8b-instruct",  # 8B -> speed
        "accounts/fireworks/models/deepseek-r1",  # reasoning -> thinking
        "accounts/fireworks/models/deepseek-v3",  # no size token -> other
    ]
    groups = classify_models("fireworks", raw)

    assert (
        "accounts/fireworks/models/llama-v3p3-70b-instruct" in groups[Tier.QUALITY_CHAT]
    )
    assert (
        "accounts/fireworks/models/mixtral-8x22b-instruct" in groups[Tier.QUALITY_CHAT]
    )
    assert "accounts/fireworks/models/qwen2p5-32b-instruct" in groups[Tier.BALANCE_CHAT]
    assert "accounts/fireworks/models/llama-v3p1-8b-instruct" in groups[Tier.SPEED_CHAT]
    assert "accounts/fireworks/models/deepseek-r1" in groups[Tier.THINKING_CHAT]
    assert "accounts/fireworks/models/deepseek-v3" in groups[Tier.OTHER]


def test_fireworks_classification_preserves_account_prefix():
    # Like Together, Fireworks' classifier must NOT strip the
    # "accounts/fireworks/models/" prefix - it's required to actually
    # call the model.
    groups = classify_models(
        "fireworks", ["accounts/fireworks/models/llama-v3p1-8b-instruct"]
    )

    assert "accounts/fireworks/models/llama-v3p1-8b-instruct" in groups[Tier.SPEED_CHAT]
    assert "llama-v3p1-8b-instruct" not in groups[Tier.SPEED_CHAT]


def test_cerebras_classification():
    raw = [
        "llama-4-maverick-17b-128e-instruct",  # codename -> quality
        "llama-4-scout-17b-16e-instruct",  # codename -> balance
        "qwen-3-32b",  # 32B -> balance
        "llama3.1-8b",  # 8B -> speed
        "gpt-oss-120b",  # reasoning-flagged -> thinking
        "some-unknown-model",  # no match -> other
    ]
    groups = classify_models("cerebras", raw)

    assert "llama-4-maverick-17b-128e-instruct" in groups[Tier.QUALITY_CHAT]
    assert "llama-4-scout-17b-16e-instruct" in groups[Tier.BALANCE_CHAT]
    assert "qwen-3-32b" in groups[Tier.BALANCE_CHAT]
    assert "llama3.1-8b" in groups[Tier.SPEED_CHAT]
    assert "gpt-oss-120b" in groups[Tier.THINKING_CHAT]
    assert "some-unknown-model" in groups[Tier.OTHER]


def test_cerebras_classification_moe_uses_first_size_token():
    # "qwen-3-235b-a22b-instruct-2507" has two size-like tokens (total
    # params "235b" and active params "a22b") - the first one found
    # (total params) should win, landing this in quality-chat.
    groups = classify_models("cerebras", ["qwen-3-235b-a22b-instruct-2507"])

    assert "qwen-3-235b-a22b-instruct-2507" in groups[Tier.QUALITY_CHAT]


def test_perplexity_classification():
    raw = [
        "sonar",  # no suffix -> speed
        "sonar-pro",  # pro -> quality
        "sonar-reasoning",  # reasoning -> thinking
        "sonar-reasoning-pro",  # reasoning-pro -> thinking
        "sonar-deep-research",  # deep-research -> thinking
        "some-unknown-model",  # no match -> other
    ]
    groups = classify_models("perplexity", raw)

    assert "sonar" in groups[Tier.SPEED_CHAT]
    assert "sonar-pro" in groups[Tier.QUALITY_CHAT]
    assert "sonar-reasoning" in groups[Tier.THINKING_CHAT]
    assert "sonar-reasoning-pro" in groups[Tier.THINKING_CHAT]
    assert "sonar-deep-research" in groups[Tier.THINKING_CHAT]
    assert "some-unknown-model" in groups[Tier.OTHER]


def test_openrouter_classification():
    raw = [
        "meta-llama/llama-3.3-70b-instruct",  # 70B -> quality
        "mistralai/mixtral-8x7b-instruct",  # MoE -> quality
        "qwen/qwen-2.5-32b-instruct",  # 32B -> balance
        "meta-llama/llama-3.1-8b-instruct",  # 8B -> speed
        "deepseek/deepseek-r1",  # reasoning -> thinking
        "openai/gpt-4o",  # no size info -> other
        "anthropic/claude-3.5-sonnet",  # no size info -> other
        "openrouter/auto",  # meta-model, no size info -> other
    ]
    groups = classify_models("openrouter", raw)

    assert "meta-llama/llama-3.3-70b-instruct" in groups[Tier.QUALITY_CHAT]
    assert "mistralai/mixtral-8x7b-instruct" in groups[Tier.QUALITY_CHAT]
    assert "qwen/qwen-2.5-32b-instruct" in groups[Tier.BALANCE_CHAT]
    assert "meta-llama/llama-3.1-8b-instruct" in groups[Tier.SPEED_CHAT]
    assert "deepseek/deepseek-r1" in groups[Tier.THINKING_CHAT]
    assert "openai/gpt-4o" in groups[Tier.OTHER]
    assert "anthropic/claude-3.5-sonnet" in groups[Tier.OTHER]
    assert "openrouter/auto" in groups[Tier.OTHER]


def test_openrouter_classification_preserves_vendor_prefix():
    # Like Together/Fireworks, OpenRouter's classifier must NOT strip the
    # "vendor/" prefix - it's required to actually call the model.
    groups = classify_models("openrouter", ["meta-llama/llama-3.1-8b-instruct"])

    assert "meta-llama/llama-3.1-8b-instruct" in groups[Tier.SPEED_CHAT]
    assert "llama-3.1-8b-instruct" not in groups[Tier.SPEED_CHAT]


def test_moonshot_classification():
    raw = [
        "moonshot-v1-128k",  # 128k context -> quality
        "kimi-k2-0711-preview",  # flagship codename -> quality
        "moonshot-v1-32k",  # 32k context -> balance
        "kimi-k2-turbo-preview",  # turbo codename -> balance
        "moonshot-v1-8k",  # 8k context -> speed
        "moonshot-v1-auto",  # dynamic context -> other
        "some-unknown-model",  # no match -> other
    ]
    groups = classify_models("moonshot", raw)

    assert "moonshot-v1-128k" in groups[Tier.QUALITY_CHAT]
    assert "kimi-k2-0711-preview" in groups[Tier.QUALITY_CHAT]
    assert "moonshot-v1-32k" in groups[Tier.BALANCE_CHAT]
    assert "kimi-k2-turbo-preview" in groups[Tier.BALANCE_CHAT]
    assert "moonshot-v1-8k" in groups[Tier.SPEED_CHAT]
    assert "moonshot-v1-auto" in groups[Tier.OTHER]
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
