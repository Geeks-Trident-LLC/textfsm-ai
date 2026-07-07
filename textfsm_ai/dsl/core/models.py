# textfsm_ai/dsl/core/models.py

from dataclasses import dataclass
from typing import Dict, List, Optional

from textfsm_ai.core.serializable import Serializable
from textfsm_ai.dsl.ast.nodes import TemplateAST


@dataclass
class DSLParseResult(Serializable):
    raw_template: str
    records: List[Dict[str, str]]

    ast: Optional[TemplateAST] = None
    canonical: Optional[str] = None
    readable: Optional[str] = None
    recognizers: Optional[List[str]] = None

    name: str = ""
    ready: bool = False
    reason: Optional[str] = None


@dataclass(frozen=True)
class DSLPipeline(Serializable):
    dsl: Optional[DSLParseResult] = None
    reason: str = ""
    ready: bool = False
