# textfsm_ai/delivery/core/package.py

import json
import platform
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import textfsm

import textfsm_ai
from textfsm_ai.core.serializable import Serializable, to_dict
from textfsm_ai.core.utils.text import format_block_title, mask_middle
from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline


@dataclass
class Version(Serializable):
    python_version: str = platform.python_version()
    textfsm_version: str = textfsm.__version__
    textfsm_ai_version: str = textfsm_ai.__version__

    def to_string(self) -> str:
        return "\n".join(
            [
                format_block_title("Versions"),
                f"Python     : {self.python_version}",
                f"TextFSM    : {self.textfsm_version}",
                f"TextFSM-AI : {self.textfsm_ai_version}",
                format_block_title("Versions", ended=True),
            ]
        )


@dataclass
class LLMInfo(Serializable):
    provider_name: str = ""
    model: str = ""
    api_key: str = ""
    endpoint: str = ""
    api_version: str = ""
    region: str = ""
    project: str = ""

    def to_string(self) -> str:
        """Return a clean, readable summary of LLM configuration."""
        parts = [format_block_title("LLM Info")]

        if self.provider_name == "bedrock":
            # Bedrock has no project-level api_key - boto3 resolves AWS
            # credentials on its own, so there's nothing to mask here.
            parts.extend(
                [
                    "API Key     : <not used, resolved via AWS credential chain>",
                    f"Provider    : {self.provider_name}",
                    f"Model       : {self.model}",
                    f"Region      : {self.region}",
                ]
            )
        elif self.provider_name == "vertexai":
            # Vertex AI has no project-level api_key either - the
            # google-genai SDK resolves GCP credentials (ADC) on its own.
            parts.extend(
                [
                    "API Key     : <not used, resolved via GCP ADC credential chain>",
                    f"Provider    : {self.provider_name}",
                    f"Model       : {self.model}",
                    f"Region      : {self.region}",
                    f"Project     : {self.project}",
                ]
            )
        else:
            masked_key = mask_middle(self.api_key)
            parts.extend(
                [
                    f"API Key     : {masked_key}",
                    f"Provider    : {self.provider_name}",
                ]
            )

            if self.endpoint:
                parts.extend(
                    [
                        f"Deployment  : {self.model}",
                        f"Endpoint    : {self.endpoint}",
                        f"API Version : {self.api_version}",
                    ]
                )
            else:
                parts.append(f"Model       : {self.model}")

        parts.append(format_block_title("LLM Info", ended=True))

        return "\n".join(parts)


@dataclass
class LLMResponse(Serializable):
    raw: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    max_retries: int = 1

    def to_string(self) -> str:
        """Return a readable summary of the LLM response with masked raw payload."""
        parts = [
            format_block_title("LLM Response"),
            f"Duration (ms) : {self.duration_ms}",
            f"Max Retries   : {self.max_retries}",
            "Raw           :",
        ]

        # Pretty-print raw JSON payload
        raw_text = json.dumps(
            to_dict(self.raw), indent=2, sort_keys=True, ensure_ascii=False
        )
        parts.append(raw_text)

        parts.append(
            format_block_title("LLM Response", ended=True),
        )

        return "\n".join(parts)


@dataclass
class LLMStructuredResponse(Serializable):
    template: str = ""
    records: List[Dict[str, str]] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    handling: List[str] = field(default_factory=list)

    def to_string(self) -> str:
        """Return a readable summary of the structured LLM output."""
        parts = [
            format_block_title("LLM Structured Response"),
            format_block_title("Template", bar_char="+", width=2),
            f"{self.template or '<empty>'}",
            format_block_title("Template", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Records", bar_char="+", width=2),
            json.dumps(self.records, indent=2, ensure_ascii=False),
            format_block_title("Records", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Variables", bar_char="+", width=2),
            json.dumps(self.variables, indent=2, ensure_ascii=False),
            format_block_title("Variables", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Handling", bar_char="+", width=2),
            json.dumps(self.handling, indent=2, ensure_ascii=False),
            format_block_title("Handling", bar_char="+", width=2, ended=True),
            "",
            format_block_title("LLM Structured Response", ended=True),
            "",
        ]
        return "\n".join(parts)


@dataclass
class Usage(Serializable):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    llm_duration_ms: float = 0.0
    currency: str = "dollar"
    input_per_million: float = 0.0
    output_per_million: float = 0.0
    estimated_cost: float = 0.0
    warning: str = ""

    def to_string(self) -> str:
        """Return a readable summary of token usage and cost estimation."""
        parts = [
            format_block_title("LLM Usage"),
            f"Input Tokens       : {self.input_tokens}",
            f"Output Tokens      : {self.output_tokens}",
            f"Total Tokens       : {self.total_tokens}",
            f"LLM Duration (ms)  : {self.llm_duration_ms}",
            f"Input per Million  : {self.input_per_million}",
            f"Output per Million : {self.output_per_million}",
            f"Estimated Cost     : ${self.estimated_cost:.6f}",
        ]

        if self.warning:
            parts.append(f"Warning            : {self.warning}")

        parts.append(format_block_title("LLM Usage", ended=True))

        return "\n".join(parts)


@dataclass
class Output(Serializable):
    raw_template: str = ""
    template: str = ""
    readable_dsl: str = ""
    recognizers: List[str] = field(default_factory=list)

    def to_string(self) -> str:
        """Return a readable summary of the final DSL output."""
        parts = [
            format_block_title("Output"),
            format_block_title("Raw Template", bar_char="+", width=2),
            f"{self.raw_template or '<empty>'}",
            format_block_title("Raw Template", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Template", bar_char="+", width=2),
            f"{self.template or '<empty>'}",
            format_block_title("Template", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Readable DSL", bar_char="+", width=2),
            self.readable_dsl or "<empty>",
            format_block_title("Readable DSL", bar_char="+", width=2, ended=True),
            "",
            format_block_title("Recognizers", bar_char="+", width=2),
        ]

        if self.recognizers:
            parts.append(
                json.dumps(
                    self.recognizers, indent=2, sort_keys=True, ensure_ascii=False
                )
            )
        else:
            parts.append("<none>")

        parts.append(
            format_block_title("Recognizers", bar_char="+", width=2, ended=True)
        )
        parts.append(
            format_block_title("Output", ended=True),
        )

        return "\n".join(parts)


@dataclass
class Status(Serializable):
    state: str = ""
    errors: List[str] = field(default_factory=list)
    passed: bool = False

    def __bool__(self) -> bool:
        return self.passed

    @property
    def error(self):
        return "\n".join(self.errors)

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

    def to_string(self) -> str:
        """Return a readable summary of the status outcome."""
        title = self.state or "<no-state>"

        if self.passed:
            return f"=== SUCCESS: {title} ==="

        if self.errors:
            error_block = "\n".join(self.errors)
        else:
            error_block = "<none>"

        return f"=== FAIL: {title} ===\n{error_block}"


@dataclass
class Quiet(Serializable):
    template: str = ""
    status: Status = field(default_factory=Status)

    def to_string(self) -> str:
        """Return template on success, or a formatted status message on failure."""
        if self.status.passed:
            return self.template or "<empty-template>"
        return self.status.to_string()


@dataclass
class Default(Serializable):
    output: Output = field(default_factory=Output)
    status: Status = field(default_factory=Status)

    def to_string(self) -> str:
        """Return output on success, or a formatted status message on failure."""
        if self.status.passed:
            text = self.output.to_string()
            return text or "<empty-output>"
        return self.status.to_string()


@dataclass
class Info(Serializable):
    version: Version = field(default_factory=Version)
    llm_info: LLMInfo = field(default_factory=LLMInfo)
    usage: Usage = field(default_factory=Usage)
    llm_structured_response: LLMStructuredResponse = field(
        default_factory=LLMStructuredResponse
    )
    output: Output = field(default_factory=Output)
    status: Status = field(default_factory=Status)

    def to_string(self) -> str:
        """Return a readable summary of pipeline information."""
        parts = [
            format_block_title("Info"),
            f"Status : {'PASS' if self.status.passed else 'FAIL'}",
            "",
            self.version.to_string(),
            "",
            self.llm_info.to_string(),
            "",
            self.usage.to_string(),
            "",
            self.llm_structured_response.to_string(),
            "",
            self.output.to_string(),
            format_block_title("Info", ended=True),
        ]
        return "\n".join(parts)


@dataclass
class Debug(Serializable):
    llm_info: Optional[LLMInfo] = None
    llm_response: Optional[LLMResponse] = None
    usage: Optional[Usage] = None
    generation_pipeline: Optional[GenerationPipeline] = None
    dsl_pipeline: Optional[DSLPipeline] = None
    version: Version = field(default_factory=Version)
    status: Status = field(default_factory=Status)
    duration_ms: float = 0.0

    def to_string(self) -> str:
        """Return a readable debug dump."""
        parts = [format_block_title("Debug")]

        parts.append(f"Status        : {'PASS' if self.status.passed else 'FAIL'}")
        parts.append(f"Duration (ms) : {self.duration_ms}")
        parts.append("")

        parts.append(self.version.to_string())
        parts.append("")

        parts.append(self.llm_info.to_string() if self.llm_info else "<none>")
        parts.append("")

        parts.append(self.llm_response.to_string() if self.llm_response else "<none>")
        parts.append("")

        parts.append(self.usage.to_string() if self.usage else "<none>")
        parts.append("")

        parts.append(format_block_title("Generation Pipeline", bar_char="+", width=2))

        parts.append(
            self.generation_pipeline.to_json() if self.generation_pipeline else "<none>"
        )
        parts.append(
            format_block_title("Generation Pipeline", bar_char="+", width=2, ended=True)
        )
        parts.append("")

        parts.append(format_block_title("DSL Pipeline", bar_char="+", width=2))
        parts.append(self.dsl_pipeline.to_json() if self.dsl_pipeline else "<none>")
        parts.append(
            format_block_title("DSL Pipeline", bar_char="+", width=2, ended=True)
        )

        parts.append(format_block_title("Debug", ended=True))

        return "\n".join(parts)


@dataclass
class DeliveryPackage:
    quiet: Quiet
    default: Default
    info: Info
    debug: Debug


@dataclass
class DeliveryOutput:
    """Formatted result of running the full generate + compile pipeline.

    Attributes:
        mode: The verbosity mode `output` was formatted for.
        output: The formatted text (or JSON, if `as_json=True` was passed).
        passed: True if the pipeline succeeded.
        error: Failure detail if `passed` is False; "" on success.
    """

    mode: DeliveryMode
    output: str = ""
    passed: bool = False
    error: str = ""

    def __bool__(self):
        return self.passed

    @property
    def exit_code(self):
        return 0 if self.passed else 1
