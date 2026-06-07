from __future__ import annotations

from typing import List

from .patterns import (
    ANTHROPIC_PATTERN,
    DEEPSEEK_NATIVE_PATTERN,
    DEEPSEEK_PATTERN_V4,
    GEMINI_PATTERN,
    OPENAI_PATTERN,
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
    if provider in ("azure", "azure-openai"):
        return classify_openai_models(raw)

    # Unknown provider → everything goes to OTHER
    groups = empty_tier_groups()
    groups[Tier.OTHER].extend(map(_normalize, raw))
    return groups
