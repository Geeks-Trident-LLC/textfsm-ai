# textfsm_ai/core/pricing.py

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pricing registry (per provider → per model family)
# Prices are per 1 million tokens. Loaded from pricing.yaml so adding a new
# provider/model doesn't require touching this module.
# ---------------------------------------------------------------------------

PRICING_DATA_PATH = Path(__file__).parent / "pricing.yaml"


def _load_pricing_table() -> Dict[str, Dict[str, Dict[str, float]]]:
    with open(PRICING_DATA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


PRICING_TABLE: Dict[str, Dict[str, Dict[str, float]]] = _load_pricing_table()


PRICING_TABLE.setdefault("azure", copy.deepcopy(PRICING_TABLE["openai"]))
PRICING_TABLE["azure"].update(
    {
        k: copy.deepcopy(v)
        for k, v in PRICING_TABLE["anthropic"].items()
        if k in ("claude-opus-4-8", "claude-haiku-4-5")
        # only models GA on Azure-hosted Foundry
    }
)
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
# Model family extractor
# ---------------------------------------------------------------------------


def extract_base_model(provider: str, full_model: str) -> str:
    """
    Extract the pricing base model (family) from a full model name.

    Returns the *longest* matching prefix from PRICING_TABLE[provider].
    """

    if provider not in PRICING_TABLE:
        return ""

    families = PRICING_TABLE[provider].keys()

    matches = [f for f in families if full_model.startswith(f)]
    if not matches:
        return ""

    # Return longest match
    return max(matches, key=len)


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
