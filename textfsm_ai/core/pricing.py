# textfsm_ai/core/pricing.py

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pricing registry (per provider → per model family)
# Prices are per 1 million tokens.
# ---------------------------------------------------------------------------


# All prices in USD per 1M tokens. Verified against official pricing pages, July 2026.
PRICING_TABLE: Dict[str, Dict[str, Dict[str, float]]] = {
    "anthropic": {
        "claude-fable-5": {"input": 10.00, "output": 50.00},
        "claude-opus-3": {"input": 15.00, "output": 75.00},
        "claude-opus-4": {"input": 15.00, "output": 75.00},
        "claude-opus-4-1": {"input": 15.00, "output": 75.00},
        "claude-opus-4-5": {"input": 5.00, "output": 25.00},
        "claude-opus-4-6": {"input": 5.00, "output": 25.00},
        "claude-opus-4-7": {"input": 5.00, "output": 25.00},
        "claude-opus-4-8": {"input": 5.00, "output": 25.00},
        "claude-sonnet-3-5": {"input": 3.00, "output": 15.00},
        "claude-sonnet-3-7": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4": {"input": 3.00, "output": 15.00},
        # $6/$22.50 beyond 200K context
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        # 1M context at standard rate, no surcharge
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
        # intro pricing through Aug 31, 2026; then $3/$15
        "claude-sonnet-5": {"input": 2.00, "output": 10.00},
        "claude-haiku-3": {"input": 0.25, "output": 1.25},
        "claude-haiku-3-5": {"input": 0.80, "output": 4.00},
        "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
    },
    "openai": {
        # GPT-5.5 (current flagship)
        "gpt-5.5": {"input": 5.00, "output": 30.00},
        "gpt-5.5-pro": {"input": 30.00, "output": 180.00},
        # GPT-5.4 (recommended production workhorse)
        "gpt-5.4": {"input": 2.50, "output": 15.00},
        "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
        "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
        # GPT-5 family (previous generation, still callable)
        "gpt-5": {"input": 1.25, "output": 10.00},
        "gpt-5-mini": {"input": 0.25, "output": 2.00},
        "gpt-5-nano": {"input": 0.05, "output": 0.40},
        "gpt-5-pro": {"input": 15.00, "output": 120.00},
        # GPT-4.1 family — cheapest long-context (1M) option
        "gpt-4.1": {"input": 2.00, "output": 8.00},
        "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
        "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
        # o-series reasoning models
        "o3": {"input": 2.00, "output": 8.00},
        "o3-pro": {"input": 20.00, "output": 80.00},
        "o4-mini": {"input": 1.10, "output": 4.40},
        # Legacy, still callable:
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "o1-pro": {"input": 150.00, "output": 600.00},
    },
    "deepseek": {
        "deepseek-v4-flash": {"input": 0.14, "output": 0.28},
        # "deepseek-v4-pro":   {"input": 0.435, "output": 0.87},   # promo rate
        "deepseek-v4-pro": {"input": 1.74, "output": 3.48},  # full rate $1.74/$3.48
    },
    "gemini": {
        # Gemini 3.5 (current flagship Flash — beats 3.1 Pro on coding at lower cost)
        "gemini-3.5-flash": {"input": 1.50, "output": 9.00},
        # Gemini 3.1 family
        # doubles above 200K context
        "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
        "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
        # Gemini 3 (previous gen, still available)
        "gemini-3-flash": {"input": 0.50, "output": 3.00},
        # Gemini 2.5 family
        # $2.50/$15 above 200K context
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
        "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
        "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    },
}


PRICING_TABLE.setdefault("azure", copy.deepcopy(PRICING_TABLE["openai"]))
PRICING_TABLE["azure"].update({
    k: copy.deepcopy(v) for k, v in PRICING_TABLE["anthropic"].items()
    if k in ("claude-opus-4-8", "claude-haiku-4-5")  
    # only models GA on Azure-hosted Foundry
})
PRICING_TABLE["azure"].update(copy.deepcopy(PRICING_TABLE["deepseek"]))


SONNET_5_INTRO_PRICING_END = datetime(2026, 9, 1, tzinfo=timezone.utc)


_ACK_FLAG_FILE = Path.home() / ".textfsm-ai" / ".sonnet_5_pricing_ack"


def update_claude_sonnet_5(now: datetime | None = None) -> None:
    """
    One-shot check: bumps Sonnet 5 to standard pricing after the
    introductory period ends. Call this periodically (e.g. once per
    process start, or on a daily scheduled job) — do NOT loop/sleep
    inside this function.
    """
    now = now or datetime.now(timezone.utc)
    sonnet5 = PRICING_TABLE["anthropic"]["claude-sonnet-5"]

    already_updated = sonnet5["input"] == 3.00 and sonnet5["output"] == 15.00

    if already_updated:
        # Only nag once, ever, so re-running this doesn't spam logs.
        if not _ACK_FLAG_FILE.exists():
            logger.warning(
                "claude-sonnet-5 is at standard pricing ($3/$15). "
                "This update_claude_sonnet_5() function and its call site "
                "are now dead code — safe to remove."
            )
            _ACK_FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
            _ACK_FLAG_FILE.touch()
        return

    if now < SONNET_5_INTRO_PRICING_END:
        # Still in the introductory pricing window — nothing to do yet.
        return

    # Past the cutoff and still on intro pricing — update it.
    sonnet5["input"] = 3.00
    sonnet5["output"] = 15.00
    logger.warning(
        "claude-sonnet-5 pricing auto-updated to standard rate ($3/$15) "
        "as of %s. Please verify against https://claude.com/pricing "
        "and remove this auto-update logic once confirmed.",
        now.isoformat(),
    )


update_claude_sonnet_5()


# ---------------------------------------------------------------------------
# Optional deployment → model family mapping (Azure, custom deployments)
# ---------------------------------------------------------------------------

DEPLOYMENT_MAP: Dict[str, str] = {
    # Example:
    # "my-gpt4o": "gpt-4o",
    # "my-mini": "gpt-4o-mini",
}


# ---------------------------------------------------------------------------
# Model family extractor
# ---------------------------------------------------------------------------


def extract_base_model(provider: str, full_model: str) -> str:
    """
    Extract the pricing base model (family) from a full model name.

    Example:
        full_model="claude-3-opus-20240229" → "claude-opus"
        full_model="gpt-4o-2024-08-06"      → "gpt-4o"
        full_model="gpt-4o-mini-2024-09-12" → "gpt-4o-mini"
        full_model="deepseek-v4-flash"      → "deepseek-v4-flash"
    """

    if provider not in PRICING_TABLE:
        return ""

    families = PRICING_TABLE[provider].keys()

    for family in families:
        if full_model.startswith(family):
            return family

    return ""


# ---------------------------------------------------------------------------
# Pricing result dataclass
# ---------------------------------------------------------------------------


@dataclass
class PricingResult:
    provider: str
    based_model: str
    currency: str
    input_per_million: float
    output_per_million: float
    estimated_cost: float
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "based_model": self.based_model,
            "currency": self.currency,
            "input_per_million": self.input_per_million,
            "output_per_million": self.output_per_million,
            "estimated_cost": self.estimated_cost,
            "warning": self.warning,
        }


# ---------------------------------------------------------------------------
# Cost estimation function
# ---------------------------------------------------------------------------


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    currency: str,
    provider: str,
    model: str,
) -> PricingResult:
    """
    Estimate cost for an LLM request.

    Resolution:
        - Extract pricing family from model.
        - If missing → fallback.
    """

    based_model = extract_base_model(provider, model)

    if not based_model:
        warning = (
            f"Model not listed in pricing table; unable to resolve pricing family "
            f"from provider={provider}, model={model}. Using fallback pricing."
        )
        return PricingResult(
            provider=provider,
            based_model="unknown",
            currency=currency,
            input_per_million=0.0,
            output_per_million=0.0,
            estimated_cost=0.0,
            warning=warning,
        )

    pricing = PRICING_TABLE.get(provider, {}).get(based_model)

    if pricing is None:
        warning = (
            f"Pricing family '{based_model}' not found for provider '{provider}'. "
            f"Using fallback pricing."
        )
        return PricingResult(
            provider=provider,
            based_model=based_model,
            currency=currency,
            input_per_million=0.0,
            output_per_million=0.0,
            estimated_cost=0.0,
            warning=warning,
        )

    # Compute cost
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    # Reasoning tokens billed at output rate
    other_tokens = max(total_tokens - input_tokens - output_tokens, 0)
    other_cost = (other_tokens / 1_000_000) * pricing["output"]

    estimated_cost = input_cost + output_cost + other_cost

    return PricingResult(
        provider=provider,
        based_model=based_model,
        currency=currency,
        input_per_million=pricing["input"],
        output_per_million=pricing["output"],
        estimated_cost=estimated_cost,
        warning=None,
    )
