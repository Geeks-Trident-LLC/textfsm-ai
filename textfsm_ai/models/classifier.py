from __future__ import annotations

import re
from typing import List

from .patterns import (
    ANTHROPIC_PATTERN,
    BEDROCK_PATTERN,
    CEREBRAS_PATTERN,
    DEEPSEEK_NATIVE_PATTERN,
    DEEPSEEK_PATTERN_V4,
    FIREWORKS_PATTERN,
    GEMINI_PATTERN,
    GROQ_PATTERN,
    MISTRAL_PATTERN,
    MOONSHOT_PATTERN,
    OPENAI_PATTERN,
    OPENROUTER_PATTERN,
    PERPLEXITY_PATTERN,
    TOGETHER_PATTERN,
    XAI_PATTERN,
)
from .tiers import Tier, empty_tier_groups


# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------
def _normalize(name: str) -> str:
    name = name.strip()
    if "/" in name:
        name = name.split("/")[-1]
    return name


# ---------------------------------------------------------
# OpenAI
# ---------------------------------------------------------
def classify_openai_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        m = OPENAI_PATTERN.match(name)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        family = m.group(1)  # e.g. "gpt-4.1", "gpt-5.4"
        suffix = m.group(2)  # e.g. "mini", "nano", "pro", "flash-lite"

        # Premium reasoning (thinking-chat)
        if family.startswith("o") or suffix == "pro":
            groups[Tier.THINKING_CHAT].append(name)
            continue

        # Quality chat (default tier)
        if suffix is None:
            groups[Tier.QUALITY_CHAT].append(name)
            continue

        # Balance
        if suffix in ("mini", "flash"):
            groups[Tier.BALANCE_CHAT].append(name)
            continue

        # Speed
        if suffix in ("nano", "flash-lite", "instant"):
            groups[Tier.SPEED_CHAT].append(name)
            continue

        groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------
def classify_gemini_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        m = GEMINI_PATTERN.match(name)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        kind = m.group(1)  # pro, flash, flash-lite, flash-image, etc.

        if kind == "pro":
            groups[Tier.QUALITY_CHAT].append(name)
        elif kind == "flash":
            groups[Tier.BALANCE_CHAT].append(name)
        elif kind == "flash-lite":
            groups[Tier.SPEED_CHAT].append(name)
        else:
            groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Anthropic
# ---------------------------------------------------------
def classify_anthropic_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        match = ANTHROPIC_PATTERN.match(name)
        if not match:
            groups[Tier.OTHER].append(name)
            continue

        family = match.group(1)  # opus, sonnet, haiku

        if family == "opus":
            groups[Tier.QUALITY_CHAT].append(name)
        elif family == "sonnet":
            groups[Tier.BALANCE_CHAT].append(name)
        elif family == "haiku":
            groups[Tier.SPEED_CHAT].append(name)
        else:
            groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# DeepSeek
# ---------------------------------------------------------
def classify_deepseek_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        # DeepSeek v4 family
        m_v4 = DEEPSEEK_PATTERN_V4.match(name)
        if m_v4:
            kind = m_v4.group(1)  # pro, flash
            if kind == "pro":
                groups[Tier.QUALITY_CHAT].append(name)
            elif kind == "flash":
                groups[Tier.BALANCE_CHAT].append(name)
            continue

        # DeepSeek native models (chat, reasoner, r1, r1-distill)
        m_native = DEEPSEEK_NATIVE_PATTERN.match(name)
        if m_native:
            kind = m_native.group(1)
            if kind == "chat":
                groups[Tier.BALANCE_CHAT].append(name)
            elif kind in ("reasoner", "r1", "r1-distill"):
                groups[Tier.THINKING_CHAT].append(name)
            continue

        groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Groq (hosts open models, classified by parameter size rather than
# a vendor-assigned tier suffix)
# ---------------------------------------------------------
def classify_groq_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        m = GROQ_PATTERN.match(name)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        # Reasoning/distilled models go to thinking-chat regardless of size
        if "distill" in name or "r1" in name or "reasoner" in name:
            groups[Tier.THINKING_CHAT].append(name)
            continue

        size = m.group(1)  # e.g. "70", "8", "8x7"

        # Mixture-of-experts sizes (e.g. "8x7") count as quality tier
        if "x" in size:
            groups[Tier.QUALITY_CHAT].append(name)
            continue

        size_num = int(size)
        if size_num >= 70:
            groups[Tier.QUALITY_CHAT].append(name)
        elif size_num >= 30:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# xAI (Grok)
# ---------------------------------------------------------
def classify_xai_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        m = XAI_PATTERN.match(name)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        suffix = m.group(1)  # mini, vision, fast, or None

        if suffix == "vision":
            groups[Tier.OTHER].append(name)
        elif suffix == "mini":
            groups[Tier.SPEED_CHAT].append(name)
        elif suffix == "fast":
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.QUALITY_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Together AI (hosts many open-model families under vendor/model
# namespaces). Deliberately does NOT use _normalize(): Together's real
# API model IDs (e.g. "meta-llama/Llama-3.3-70B-Instruct-Turbo") need
# the vendor prefix to be usable in a real API call, unlike other
# providers where a "/" prefix (if present at all) is just noise from
# a router wrapper. Stripping it here would hand back unusable model
# names from `list-models together --latest`.
# ---------------------------------------------------------
def classify_together_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(str.strip, raw):
        lname = name.lower()

        # Reasoning/distilled models go to thinking-chat regardless of size
        if "r1" in lname or "reasoner" in lname or "distill" in lname or "qwq" in lname:
            groups[Tier.THINKING_CHAT].append(name)
            continue

        m = TOGETHER_PATTERN.search(lname)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        # Mixture-of-experts sizes (e.g. "8x7b") count as quality tier
        if m.group("moe"):
            groups[Tier.QUALITY_CHAT].append(name)
            continue

        size_num = float(m.group("size"))
        if size_num >= 70:
            groups[Tier.QUALITY_CHAT].append(name)
        elif size_num >= 30:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Fireworks AI (hosts open models under
# "accounts/fireworks/models/<slug>"). Same reasoning as
# classify_together_models(): deliberately does NOT use _normalize(),
# since the "accounts/fireworks/models/" prefix is required to
# actually call the model, not noise from a router wrapper.
# ---------------------------------------------------------
def classify_fireworks_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(str.strip, raw):
        lname = name.lower()

        # Reasoning/distilled models go to thinking-chat regardless of size
        if "r1" in lname or "reasoner" in lname or "distill" in lname or "qwq" in lname:
            groups[Tier.THINKING_CHAT].append(name)
            continue

        m = FIREWORKS_PATTERN.search(lname)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        # Mixture-of-experts sizes (e.g. "8x22b") count as quality tier
        if m.group("moe"):
            groups[Tier.QUALITY_CHAT].append(name)
            continue

        size_num = float(m.group("size"))
        if size_num >= 70:
            groups[Tier.QUALITY_CHAT].append(name)
        elif size_num >= 30:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Cerebras (hosts open models under bare, un-namespaced IDs like Groq,
# so _normalize() is safe here - no vendor prefix to preserve).
# Cerebras' catalog mixes dense models named by parameter size
# (qwen-3-32b, llama3.1-8b) with Llama 4's MoE models named by
# codename (scout/maverick) whose IDs only expose *active* params
# (e.g. "17b"), not the much larger total param count - so those are
# classified by codename instead of falling through to the size regex.
# ---------------------------------------------------------
def classify_cerebras_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        lname = name.lower()

        # Reasoning-flagged models go to thinking-chat regardless of size
        if (
            "gpt-oss" in lname
            or "r1" in lname
            or "reasoner" in lname
            or "distill" in lname
            or "qwq" in lname
        ):
            groups[Tier.THINKING_CHAT].append(name)
            continue

        # Llama 4 MoE models: active-param count in the name understates
        # total capability, so classify by codename instead of size.
        if "maverick" in lname:
            groups[Tier.QUALITY_CHAT].append(name)
            continue
        if "scout" in lname:
            groups[Tier.BALANCE_CHAT].append(name)
            continue

        m = CEREBRAS_PATTERN.search(lname)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        size_num = float(m.group("size"))
        if size_num >= 70:
            groups[Tier.QUALITY_CHAT].append(name)
        elif size_num >= 30:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Perplexity (search-grounded "sonar" family, fixed small catalog with
# no parameter-size info, tiered by suffix rather than size like xAI)
# ---------------------------------------------------------
def classify_perplexity_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        m = PERPLEXITY_PATTERN.match(name)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        suffix = m.group(1)  # pro, reasoning, reasoning-pro, deep-research, or None

        if suffix == "pro":
            groups[Tier.QUALITY_CHAT].append(name)
        elif suffix in ("reasoning", "reasoning-pro", "deep-research"):
            groups[Tier.THINKING_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# OpenRouter (model aggregator re-exposing many upstream providers'
# catalogs under "vendor/model" namespaces). Deliberately does NOT
# use _normalize(): the vendor prefix is required to actually call
# the model, same reasoning as Together/Fireworks. Given how
# heterogeneous the catalog is, this only reliably classifies
# reasoning-flagged and explicitly-sized (open-weight) models;
# everything else - most proprietary models, which have no size in
# the name - falls to OTHER rather than guessing.
# ---------------------------------------------------------
def classify_openrouter_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(str.strip, raw):
        lname = name.lower()

        # Reasoning/distilled models go to thinking-chat regardless of size
        if (
            "r1" in lname
            or "reasoner" in lname
            or "distill" in lname
            or "qwq" in lname
            or "thinking" in lname
        ):
            groups[Tier.THINKING_CHAT].append(name)
            continue

        m = OPENROUTER_PATTERN.search(lname)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        # Mixture-of-experts sizes (e.g. "8x7b") count as quality tier
        if m.group("moe"):
            groups[Tier.QUALITY_CHAT].append(name)
            continue

        size_num = float(m.group("size"))
        if size_num >= 70:
            groups[Tier.QUALITY_CHAT].append(name)
        elif size_num >= 30:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Moonshot AI (Kimi). Bare, un-namespaced model IDs (no "/"), so
# _normalize() is safe here. Catalog mixes "moonshot-v1-<context>"
# variants - tiered by CONTEXT WINDOW LENGTH as a rough capability
# proxy, since it's the only signal in the name (all three are the
# same underlying model) - with the separately-branded "kimi-k2-*"
# flagship line, classified by keyword instead.
# ---------------------------------------------------------
def classify_moonshot_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        lname = name.lower()

        # Kimi K2: flagship large MoE model line, named separately from
        # the "moonshot-v1-*" context-length variants.
        if "k2" in lname:
            if "turbo" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            else:
                groups[Tier.QUALITY_CHAT].append(name)
            continue

        m = MOONSHOT_PATTERN.match(lname)
        if not m:
            groups[Tier.OTHER].append(name)
            continue

        context = m.group(1)  # 8k, 32k, 128k, or auto

        if context == "128k":
            groups[Tier.QUALITY_CHAT].append(name)
        elif context == "32k":
            groups[Tier.BALANCE_CHAT].append(name)
        elif context == "8k":
            groups[Tier.SPEED_CHAT].append(name)
        else:
            # "auto" dynamically picks context length, doesn't fit a
            # fixed tier
            groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Mistral AI. Bare, un-namespaced model IDs, so _normalize() is safe
# here. Catalog spans several sub-brands (mistral-/magistral-/
# ministral-/open-mistral-/codestral/pixtral-) with no shared numeric
# size scheme, so MISTRAL_PATTERN only validates "is this a known
# Mistral model shape" and tier assignment is done via keyword checks.
# ---------------------------------------------------------
def classify_mistral_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(_normalize, raw):
        lname = name.lower()

        if not MISTRAL_PATTERN.match(lname):
            groups[Tier.OTHER].append(name)
            continue

        # Magistral: Mistral's reasoning-focused model line
        if "magistral" in lname:
            groups[Tier.THINKING_CHAT].append(name)
        # Codestral/Pixtral: code/vision-specialized, don't fit chat tiers
        elif "codestral" in lname or "pixtral" in lname:
            groups[Tier.OTHER].append(name)
        elif "large" in lname:
            groups[Tier.QUALITY_CHAT].append(name)
        elif "medium" in lname:
            groups[Tier.BALANCE_CHAT].append(name)
        else:
            # small, ministral, open-mistral-nemo
            groups[Tier.SPEED_CHAT].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Amazon Bedrock. A model AGGREGATOR like OpenRouter, but re-hosting
# vendors under "vendor.model-vN:M" IDs. Deliberately does NOT use
# _normalize(): the "vendor." prefix is required to actually call the
# model via converse(modelId=...), same reasoning as Together/Fireworks/
# OpenRouter. Each hosted vendor has its own naming scheme, so tiering
# is a per-vendor dispatch rather than one shared rule:
#   - anthropic.*: opus/sonnet/haiku keywords (mirrors
#     classify_anthropic_models())
#   - meta.*: scout/maverick codenames first (Llama 4 MoE, active-param
#     count in the name would misclassify them, same reasoning as
#     Cerebras), then falls back to a parameter-size search for dense
#     Llama models (e.g. "llama3-1-8b-instruct")
#   - mistral.*: large/medium/small keywords (mirrors
#     classify_mistral_models())
#   - cohere.*: plus/light keywords
#   - amazon.*: Titan's premier/express/lite keywords
#   - ai21.* and anything else matching the vendor namespace but no
#     known keyword: OTHER, rather than guessing
# ---------------------------------------------------------
def classify_bedrock_models(raw: List[str]):
    groups = empty_tier_groups()

    for name in map(str.strip, raw):
        lname = name.lower()

        if not BEDROCK_PATTERN.match(lname):
            groups[Tier.OTHER].append(name)
            continue

        vendor = lname.split(".", 1)[0]

        if vendor == "anthropic":
            if "opus" in lname:
                groups[Tier.QUALITY_CHAT].append(name)
            elif "sonnet" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            elif "haiku" in lname:
                groups[Tier.SPEED_CHAT].append(name)
            else:
                groups[Tier.OTHER].append(name)

        elif vendor == "meta":
            if "maverick" in lname:
                groups[Tier.QUALITY_CHAT].append(name)
            elif "scout" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            else:
                m = re.search(r"([0-9]+)b", lname)
                if not m:
                    groups[Tier.OTHER].append(name)
                else:
                    size_num = int(m.group(1))
                    if size_num >= 70:
                        groups[Tier.QUALITY_CHAT].append(name)
                    elif size_num >= 30:
                        groups[Tier.BALANCE_CHAT].append(name)
                    else:
                        groups[Tier.SPEED_CHAT].append(name)

        elif vendor == "mistral":
            if "large" in lname:
                groups[Tier.QUALITY_CHAT].append(name)
            elif "medium" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            elif "small" in lname:
                groups[Tier.SPEED_CHAT].append(name)
            else:
                groups[Tier.OTHER].append(name)

        elif vendor == "cohere":
            if "plus" in lname:
                groups[Tier.QUALITY_CHAT].append(name)
            elif "light" in lname:
                groups[Tier.SPEED_CHAT].append(name)
            elif "command-r" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            else:
                groups[Tier.OTHER].append(name)

        elif vendor == "amazon":
            if "premier" in lname:
                groups[Tier.QUALITY_CHAT].append(name)
            elif "express" in lname:
                groups[Tier.BALANCE_CHAT].append(name)
            elif "lite" in lname:
                groups[Tier.SPEED_CHAT].append(name)
            else:
                groups[Tier.OTHER].append(name)

        else:
            # ai21 and any other Bedrock vendor namespace without a
            # known keyword scheme yet.
            groups[Tier.OTHER].append(name)

    for g in groups.values():
        g.sort(reverse=True)
    return groups


# ---------------------------------------------------------
# Unified entry point
# ---------------------------------------------------------
def classify_models(provider: str, raw: List[str]):
    provider = provider.lower()

    if provider == "openai":
        return classify_openai_models(raw)
    if provider == "gemini":
        return classify_gemini_models(raw)
    if provider == "anthropic":
        return classify_anthropic_models(raw)
    if provider == "deepseek":
        return classify_deepseek_models(raw)
    if provider == "groq":
        return classify_groq_models(raw)
    if provider == "xai":
        return classify_xai_models(raw)
    if provider == "together":
        return classify_together_models(raw)
    if provider == "fireworks":
        return classify_fireworks_models(raw)
    if provider == "cerebras":
        return classify_cerebras_models(raw)
    if provider == "perplexity":
        return classify_perplexity_models(raw)
    if provider == "openrouter":
        return classify_openrouter_models(raw)
    if provider == "moonshot":
        return classify_moonshot_models(raw)
    if provider == "mistral":
        return classify_mistral_models(raw)
    if provider == "bedrock":
        return classify_bedrock_models(raw)
    if provider in ("azure", "azure-openai"):
        return classify_openai_models(raw)

    # Unknown provider → everything goes to OTHER
    groups = empty_tier_groups()
    groups[Tier.OTHER].extend(map(_normalize, raw))
    return groups
