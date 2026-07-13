"""Result types returned by the functions in :mod:`textfsm_ai.api`."""

from dataclasses import dataclass, field
from typing import Dict, List

from textfsm_ai.core.serializable import Serializable
from textfsm_ai.dsl.ast.nodes import TemplateAST


@dataclass
class LLMResult(Serializable):
    """Result of asking an LLM to turn a sample into a template.

    Attributes:
        template: The LLM-authored TextFSM template ("" if generation failed).
        records: Records the LLM claims to have parsed from the sample.
        variables: Per-variable explanations the LLM provided.
        handling: Notes on how the LLM handled ambiguous or edge-case lines.
        reason: Failure reason if `ready` is False; "" on success.
        ready: True if generation succeeded.
    """

    template: str = ""
    records: List[Dict[str, str]] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    handling: List[str] = field(default_factory=list)
    reason: str = ""
    ready: bool = False


@dataclass
class DSLResult(Serializable):
    """Result of compiling a template into ast/canonical/readable/recognizers.

    Attributes:
        ast: The parsed template AST (an empty `TemplateAST()` on failure).
        canonical: The canonical (regex-expanded) TextFSM template.
        readable: The human-readable DSL form of the template.
        recognizers: Regex patterns that detect this block of text.
        reason: Failure reason if `ready` is False; "" on success.
        ready: True if compiling succeeded.
    """

    ast: TemplateAST = field(default_factory=TemplateAST)
    canonical: str = ""
    readable: str = ""
    recognizers: List[str] = field(default_factory=list)
    reason: str = ""
    ready: bool = False
