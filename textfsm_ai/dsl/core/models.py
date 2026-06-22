# textfsm_ai/dsl/core/models.py

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from textfsm_ai.core.serializable import Serializable


@dataclass(frozen=True)
class DSLExtractorResult(Serializable):
    template: str = ""
    variables: Optional[List[Dict[str, str]]] = None
    states: Optional[List[Dict[str, str]]] = None
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class CanonicalTemplate(Serializable):
    """Canonical, normalized representation of a TextFSM template."""

    llm_template: str
    template: str
    records: Optional[List[Dict[str, Any]]] = None
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class MachineDSL(Serializable):
    """Machine-readable DSL structure derived from a canonical template."""

    canonical: CanonicalTemplate
    dsl: DSLExtractorResult
    version: str = "1.0"
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class HumanDSL(Serializable):
    """Human-readable DSL text plus optional context."""

    human_dsl: str
    template: Optional[str] = None
    sample: Optional[str] = None
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class RecognizerPatterns(Serializable):
    """Patterns recognized from DSL/template/sample for classification or routing."""

    dsl: Optional[DSLExtractorResult]
    template: Optional[str]
    sample: Optional[str]
    patterns: str = ""
    debug_info: Optional[Dict[str, Any]] = None
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class HumanDSLResult(Serializable):
    template: str = ""
    variables: Optional[list] = None
    states: Optional[list] = None
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class DSLStage(Serializable):
    name: str
    result: Any
    reason: str = ""
    ready: bool = False


@dataclass(frozen=True)
class DSLPipeline(Serializable):
    stages: list
    last_stage: Any
    reason: str = ""
    ready: bool = False
