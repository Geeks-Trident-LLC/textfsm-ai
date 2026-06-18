# textfsm_ai/generation/core/models.py

from dataclasses import dataclass
from typing import Any, Optional

from textfsm_ai.core.serializable import Serializable


# ----------------------------------
# Response
# ----------------------------------
@dataclass(frozen=True)
class LLMRawResponse(Serializable):
    raw: dict[str, Any]
    reason: str = ""
    ready: bool = True


@dataclass(frozen=True)
class LLMResponse(Serializable):
    content: str
    prompt: str
    provider: str
    model: str

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    duration_ms: Optional[int] = None
    sent_at: Optional[str] = None
    received_at: Optional[str] = None

    raw: Optional[Any] = None
    reason: str = ""
    ready: bool = False


@dataclass
class StructuredResponse(Serializable):
    template: str
    records: list
    variables: dict
    handling: list
    response: LLMResponse
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class TemplateValidationResult(Serializable):
    template: str
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class TemplateFindingResult(Serializable):
    template: str
    records: list
    sample: str
    findings: list[str]
    reason: str = ""
    ready: bool = False


@dataclass
class GenerationResult(Serializable):
    template: str
    records: list
    metadata: StructuredResponse
    reason: str = ""
    ready: bool = False


@dataclass
class GenerationControllerResult(Serializable):
    model: str
    stages: list
    last_stage: GenerationResult
    sample: str
    attempts: int = 0
    max_retries: int = 1
    reason: str = ""
    ready: bool = False
