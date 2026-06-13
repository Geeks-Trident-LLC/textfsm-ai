# textfsm_ai/dsl/core/models.py

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CanonicalTemplate:
    """Canonical, normalized representation of a TextFSM template."""

    raw_template: str
    canonical_template: str
    records_sample: Optional[List[Dict[str, Any]]] = None


@dataclass(frozen=True)
class MachineDSL:
    """Machine-readable DSL structure derived from a canonical template."""

    canonical_template: CanonicalTemplate
    ast: Any  # replace with concrete AST type when available
    version: str = "1.0"


@dataclass(frozen=True)
class HumanDSL:
    """Human-readable DSL text plus optional context."""

    dsl_text: str
    template_preview: Optional[str] = None
    sample: Optional[str] = None


@dataclass(frozen=True)
class RecognizerPatterns:
    """Patterns recognized from DSL/template/sample for classification or routing."""

    dsl: Optional[MachineDSL]
    template: Optional[CanonicalTemplate]
    sample: Optional[str]
    patterns: List[str]
    debug_info: Optional[Dict[str, Any]] = None
