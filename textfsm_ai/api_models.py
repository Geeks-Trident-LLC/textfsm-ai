# textfsm_ai/api_models.py

from dataclasses import dataclass, field
from typing import Dict, List

from textfsm_ai.core.serializable import Serializable
from textfsm_ai.dsl.ast.nodes import TemplateAST


@dataclass
class LLMResult(Serializable):
    template: str = ""
    records: List[Dict[str, str]] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    handling: List[str] = field(default_factory=list)
    reason: str = ""
    ready: bool = False


@dataclass
class DSLResult(Serializable):
    ast: TemplateAST = field(default_factory=TemplateAST)
    canonical: str = ""
    readable: str = ""
    recognizers: List[str] = field(default_factory=list)
    reason: str = ""
    ready: bool = False
