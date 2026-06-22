# textfsm_ai/delivery/core/package.py

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from textfsm_ai.core.serializable import Serializable
from textfsm_ai.dsl.core.models import DSLExtractorResult

from .modes import DeliveryMode


@dataclass
class DeliveryGeneral(Serializable):
    """General metadata included in default/info/debug modes."""

    textfsm_version: str
    textfsm_ai_version: str
    model: str
    created_at: str

    def __init__(
        self,
        *,
        textfsm_version: str,
        textfsm_ai_version: str,
        model: str,
        created_at: str,
    ):
        self.textfsm_version = textfsm_version
        self.textfsm_ai_version = textfsm_ai_version
        self.model = model
        self.created_at = created_at


@dataclass
class DeliveryTemplate(Serializable):
    canonical_template: Optional[str]
    human_template_dsl: Optional[str]

    def __init__(
        self,
        *,
        canonical_template: Optional[str],
        human_template_dsl: Optional[str],
    ):
        self.canonical_template = canonical_template
        self.human_template_dsl = human_template_dsl


@dataclass
class DeliveryExplanation(Serializable):
    variable_definitions: Optional[dict]
    llm_parsing_explanation: Optional[list]
    template_generation_explanation: Optional[str]

    def __init__(
        self,
        *,
        variable_definitions: Optional[dict],
        llm_parsing_explanation: Optional[list],
        template_generation_explanation: Optional[str],
    ):
        self.variable_definitions = variable_definitions
        self.llm_parsing_explanation = llm_parsing_explanation
        self.template_generation_explanation = template_generation_explanation


@dataclass
class DeliveryStatus(Serializable):
    state: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __init__(
        self,
        *,
        state: str,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
    ):
        self.state = state
        self.warnings = warnings or []
        self.errors = errors or []


@dataclass
class DeliveryUsage(Serializable):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    llm_duration_ms: Optional[float] = None
    estimated_cost: Optional[float] = None
    duration_ms: Optional[int] = None

    def __init__(
        self,
        *,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        llm_duration_ms: Optional[float] = None,
        estimated_cost: Optional[float] = None,
        duration_ms: Optional[int] = None,
    ):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.llm_duration_ms = llm_duration_ms
        self.estimated_cost = estimated_cost
        self.duration_ms = duration_ms


@dataclass
class DeliveryDebug(Serializable):
    raw_llm_output: Optional[str] = None
    cleaned_template: Optional[str] = None
    canonical_template_internal: Optional[str] = None
    machine_dsl: Optional[DSLExtractorResult] = None
    human_template_dsl_internal: Optional[str] = None
    recognizer_pattern: str = ""
    validation_log: List[str] = field(default_factory=list)
    canonicalization_log: List[str] = field(default_factory=list)
    literal_regex_trace: List[str] = field(default_factory=list)

    def __init__(
        self,
        *,
        raw_llm_output: Optional[str] = None,
        cleaned_template: Optional[str] = None,
        canonical_template_internal: Optional[str] = None,
        machine_dsl: Optional[DSLExtractorResult] = None,
        human_template_dsl_internal: Optional[str] = None,
        recognizer_pattern: str = "",
        validation_log: Optional[List[str]] = None,
        canonicalization_log: Optional[List[str]] = None,
        literal_regex_trace: Optional[List[str]] = None,
    ):
        self.raw_llm_output = raw_llm_output
        self.cleaned_template = cleaned_template
        self.canonical_template_internal = canonical_template_internal
        self.machine_dsl = machine_dsl
        self.human_template_dsl_internal = human_template_dsl_internal
        self.recognizer_pattern = recognizer_pattern
        self.validation_log = validation_log or []
        self.canonicalization_log = canonicalization_log or []
        self.literal_regex_trace = literal_regex_trace or []


@dataclass
class DeliveryPackage(Serializable):
    mode: DeliveryMode
    general: Optional[DeliveryGeneral]
    template: DeliveryTemplate
    explanation: Optional[DeliveryExplanation]
    status: DeliveryStatus
    usage: Optional[DeliveryUsage]
    debug: Optional[DeliveryDebug]

    def __init__(
        self,
        *,
        mode: DeliveryMode,
        general: Optional[DeliveryGeneral],
        template: DeliveryTemplate,
        explanation: Optional[DeliveryExplanation],
        status: DeliveryStatus,
        usage: Optional[DeliveryUsage],
        debug: Optional[DeliveryDebug],
    ):
        self.mode = mode
        self.general = general
        self.template = template
        self.explanation = explanation
        self.status = status
        self.usage = usage
        self.debug = debug

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)
