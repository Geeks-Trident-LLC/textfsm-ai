# textfsm_ai/generation/core/models.py

from dataclasses import dataclass
from typing import Any, Optional

from textfsm_ai.core.serializable import Serializable


@dataclass(frozen=True)
class OnePassResult(Serializable):
    """Result of the one-pass generation engine."""

    prompt: str
    response: str
    model: str
    provider: str
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class TwoPassResult(Serializable):
    """Result of the two-pass generation engine."""

    prompt_free: str
    response_free: str
    prompt_structured: str
    response_structured: str
    model: str
    provider: str
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class FallbackResult(Serializable):
    """Result of fallback selection between one-pass and two-pass."""

    winner: str  # "one_pass" or "two_pass"
    reason: str
    result: Any  # OnePassResult or TwoPassResult


@dataclass
class LLMRunResult(Serializable):
    provider: str
    model: str
    sample: str
    prompt: str
    response: str
    next_prompt: Optional[str] = None
    next_response: Optional[str] = None


@dataclass
class StructuredResult(Serializable):
    template: str  # extracted textfsm_template
    data: dict  # full parsed JSON dict
    llm_run_result: LLMRunResult


@dataclass
class GenerationResult(Serializable):
    template: str
    status: str
    structured: StructuredResult
    # def __init__(self, template: str, status: str, structured: StructuredResult):
    #     self.template = template  # final template (raw or cleaned)
    #     self.status = status  # "valid_raw", "cleaned", "invalid"
    #     self.structured = structured  # StructuredResult

    def is_success(self) -> bool:
        return self.status in ("valid_raw", "cleaned")

    def is_failure(self) -> bool:
        return self.status == "invalid"
