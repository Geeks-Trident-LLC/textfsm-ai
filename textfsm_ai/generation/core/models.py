from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class OnePassResult:
    """Result of the one-pass generation engine."""

    prompt: str
    response: str
    model: str
    provider: str
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class TwoPassResult:
    """Result of the two-pass generation engine."""

    prompt_free: str
    response_free: str
    prompt_structured: str
    response_structured: str
    model: str
    provider: str
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class FallbackResult:
    """Result of fallback selection between one-pass and two-pass."""

    winner: str  # "one_pass" or "two_pass"
    reason: str
    result: Any  # OnePassResult or TwoPassResult
