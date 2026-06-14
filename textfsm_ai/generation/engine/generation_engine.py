from textfsm_ai.generation.core.models import (
    FallbackResult,
    OnePassResult,
    TwoPassResult,
)
from textfsm_ai.generation.engine.fallback import run as _run_fallback
from textfsm_ai.generation.engine.one_pass import run as _run_one_pass
from textfsm_ai.generation.engine.two_pass import run as _run_two_pass


def one_pass(api_key: str, model: str, sample: str) -> OnePassResult:
    """Stateless one-pass generation."""
    return _run_one_pass(api_key=api_key, model=model, sample=sample)


def two_pass(api_key: str, model: str, sample: str) -> TwoPassResult:
    """Stateless two-pass generation."""
    return _run_two_pass(api_key=api_key, model=model, sample=sample)


def fallback(one: OnePassResult, two: TwoPassResult) -> FallbackResult:
    """Stateless fallback selection."""
    return _run_fallback(one, two)
