# textfsm_ai/delivery/core/package.py

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from textfsm_ai.core.serializable import Serializable

from .modes import DeliveryMode

MachineDSL = Dict[str, Any]
RecognizerDSL = List[str]


@dataclass(kw_only=True)
class DeliveryGeneral(Serializable):
    """General metadata included in default/info/debug modes."""

    textfsm_version: str
    textfsm_ai_version: str
    model: str
    created_at: str


@dataclass(kw_only=True)
class DeliveryTemplate(Serializable):
    """User-facing template outputs."""

    canonical_template: str
    human_template_dsl: str

    def __post_init__(self):
        if not self.canonical_template.strip():
            raise ValueError("canonical_template cannot be empty")
        if not self.human_template_dsl.strip():
            raise ValueError("human_template_dsl cannot be empty")


@dataclass(kw_only=True)
class DeliveryExplanation(Serializable):
    """LLM explanations included in default/info/debug modes."""

    variable_definitions: str
    llm_parsing_explanation: str
    template_generation_explanation: str


@dataclass(kw_only=True)
class DeliveryStatus(Serializable):
    """Pipeline status and warnings/errors."""

    state: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class DeliveryUsage(Serializable):
    """Token usage and cost information (info/debug modes)."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Optional[float] = None
    duration_ms: Optional[int] = None


@dataclass(kw_only=True)
class DeliveryDebug(Serializable):
    """Full debug information (debug mode only)."""

    raw_llm_output: Optional[str] = None
    cleaned_template: Optional[str] = None
    canonical_template_internal: Optional[str] = None
    machine_dsl: MachineDSL = field(default_factory=dict)
    human_template_dsl_internal: Optional[str] = None
    recognizer_dsl: RecognizerDSL = field(default_factory=list)
    validation_log: List[str] = field(default_factory=list)
    canonicalization_log: List[str] = field(default_factory=list)
    literal_regex_trace: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class DeliveryPackage(Serializable):
    """Final assembled output of the entire textfsm-ai pipeline."""

    mode: DeliveryMode
    general: Optional[DeliveryGeneral]
    template: DeliveryTemplate
    explanation: Optional[DeliveryExplanation]
    status: DeliveryStatus
    usage: Optional[DeliveryUsage]
    debug: Optional[DeliveryDebug]

    def as_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-safe dictionary."""
        return asdict(self)
