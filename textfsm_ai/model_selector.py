# textfsm_ai/model_selector.py

import re
from typing import List

from textfsm_ai.providers.anthropic_provider import list_anthropic_models
from textfsm_ai.providers.deepseek_provider import list_deepseek_models
from textfsm_ai.providers.gemini_provider import list_gemini_models
from textfsm_ai.providers.openai_provider import list_openai_models

# -------------------------
# Precompiled regex patterns
# -------------------------

OPENAI_CHAT_RE = re.compile(
    r"^gpt-[0-9]+(\.\d+)?(-(mini|nano|pro|thinking|instant|flash-lite|flash))?$",
    re.IGNORECASE,
)

GEMINI_CHAT_RE = re.compile(
    r"^gemini-[0-9]+(\.\d+)?-(pro|flash-lite|flash)$",
    re.IGNORECASE,
)

ANTHROPIC_CHAT_RE = re.compile(
    r"^claude-(opus|sonnet|haiku)-[0-9]+-\d+(-\d{6})?$",
    re.IGNORECASE,
)

DEEPSEEK_CHAT_RE = re.compile(
    r"^deepseek-v\d+-(flash|pro)$",
    re.IGNORECASE,
)


# -------------------------
# Chat model detection
# -------------------------


def is_chat_model(provider: str, model: str) -> bool:
    name = model.lower()

    if provider == "openai":
        return bool(OPENAI_CHAT_RE.match(name))

    if provider == "gemini":
        return bool(GEMINI_CHAT_RE.match(name))

    if provider == "anthropic":
        return bool(ANTHROPIC_CHAT_RE.match(name))

    if provider == "deepseek":
        return bool(DEEPSEEK_CHAT_RE.match(name))

    return False


# -------------------------
# Provider model listing
# -------------------------


def list_models(provider: str, api_key: str) -> List[str]:
    if provider == "openai":
        return list_openai_models(api_key)
    if provider == "gemini":
        return list_gemini_models(api_key)
    if provider == "anthropic":
        return list_anthropic_models(api_key)
    if provider == "deepseek":
        return list_deepseek_models(api_key)
    raise ValueError(f"Unknown provider: {provider}")


# -------------------------
# Model selection
# -------------------------


def get_model(provider: str, api_key: str, tier: str) -> str:
    models = list_models(provider, api_key)
    models = [m.split("/")[-1] for m in models]
    models = [m for m in models if is_chat_model(provider, m)]

    if not models:
        raise RuntimeError(f"No valid chat models for provider '{provider}'")

    return select_model_by_tier(provider, models, tier)


def select_model_by_tier(provider: str, models: list[str], tier: str) -> str:
    tier = tier.lower()

    # -------------------------
    # Anthropic
    # -------------------------
    if provider == "anthropic":
        if tier in ("quality", "quality-reasoning"):
            prefix = "claude-opus-"
        elif tier in ("balance", "balance-reasoning"):
            prefix = "claude-sonnet-"
        else:
            prefix = "claude-haiku-"

        candidates = [m for m in models if m.startswith(prefix)]
        if not candidates:
            raise RuntimeError(f"No {prefix} models found for tier '{tier}'")
        return sorted(candidates, reverse=True)[0]

    # -------------------------
    # OpenAI GPT
    # -------------------------
    if provider == "openai":
        if tier == "quality":
            suffix = ""
        elif tier == "balance":
            suffix = "-mini"
        elif tier == "fast":
            suffix = "-nano"
        elif tier == "quality-reasoning":
            suffix = "-pro"
        elif tier == "balance-reasoning":
            suffix = "-thinking"
        else:
            suffix = "-instant"

        candidates = [m for m in models if m.endswith(suffix)]
        if not candidates:
            raise RuntimeError(
                f"No GPT models matching suffix '{suffix}' for tier '{tier}'"
            )
        return sorted(candidates, reverse=True)[0]

    # -------------------------
    # Gemini
    # -------------------------
    if provider == "gemini":
        if tier in ("quality", "quality-reasoning"):
            suffix = "-pro"
        elif tier in ("balance", "balance-reasoning"):
            suffix = "-flash"
        else:
            suffix = "-flash-lite"

        candidates = [m for m in models if m.endswith(suffix)]
        if not candidates:
            raise RuntimeError(
                f"No Gemini models matching suffix '{suffix}' for tier '{tier}'"
            )
        return sorted(candidates, reverse=True)[0]

    # -------------------------
    # DeepSeek
    # -------------------------
    if provider == "deepseek":
        if tier.startswith("quality"):
            suffix = "-pro"
        else:
            suffix = "-flash"

        candidates = [m for m in models if m.endswith(suffix)]
        if not candidates:
            raise RuntimeError(
                f"No DeepSeek models matching suffix '{suffix}' for tier '{tier}'"
            )
        return sorted(candidates, reverse=True)[0]

    raise ValueError(f"Unknown provider '{provider}'")
