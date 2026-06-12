from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .modes import DeliveryMode


@dataclass
class DeliveryGeneral:
    textfsm_version: str
    textfsm_ai_version: str
    model: str
    created_at: str


@dataclass
class DeliveryTemplate:
    canonical_template: str
    human_template_dsl: str


@dataclass
class DeliveryExplanation:
    variable_definitions: str
    llm_parsing_explanation: str
    template_generation_explanation: str


@dataclass
class DeliveryStatus:
    state: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class DeliveryUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Optional[float] = None
    duration_ms: Optional[int] = None


@dataclass
class DeliveryDebug:
    raw_llm_output: Optional[str] = None
    cleaned_template: Optional[str] = None
    canonical_template_internal: Optional[str] = None
    machine_dsl: Optional[Dict[str, Any]] = None
    human_template_dsl_internal: Optional[str] = None
    recognizer_dsl: Optional[List[str]] = None
    validation_log: Optional[List[str]] = None
    canonicalization_log: Optional[List[str]] = None
    literal_regex_trace: Optional[List[str]] = None


@dataclass
class DeliveryPackage:
    mode: DeliveryMode
    general: Optional[DeliveryGeneral]
    template: DeliveryTemplate
    explanation: Optional[DeliveryExplanation]
    status: DeliveryStatus
    usage: Optional[DeliveryUsage]
    debug: Optional[DeliveryDebug]
