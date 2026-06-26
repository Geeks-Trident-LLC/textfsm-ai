# textfsm_ai/dsl/ast/nodes.py

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PatternItem:
    """Base class for all pattern node items."""

    raw: str
    textfsm_repr: str
    expression: str
    regex: str


@dataclass
class StartNode(PatternItem):
    pass


@dataclass
class EndNode(PatternItem):
    pass


@dataclass
class SpacerNode(PatternItem):
    pass


@dataclass
class LiteralNode(PatternItem):
    pass


@dataclass
class CallNode(PatternItem):
    pass


@dataclass
class VarNode(PatternItem):
    pass


@dataclass
class PatternNode:
    items: List[PatternItem]


@dataclass
class Action:
    line_action: Optional[str] = None  # Next | Continue
    record_action: Optional[str] = None  # Record | NoRecord | Clear | Clearall
    state: Optional[str] = None  # optional state transition
    error_pattern: Optional[str] = None  # for -> Error <regex>
    eof_action: bool = False  # for -> EOF


@dataclass
class RuleNode:
    pattern: PatternNode
    actions: List[Action]


@dataclass
class StateNode:
    name: str
    rules: List[RuleNode] = field(default_factory=list)


@dataclass
class ValueNode:
    name: str
    regex: str
    options: Optional[List[str]]
    infer: Optional[VarNode] = None


@dataclass
class TemplateAST:
    # fill with ValueNode in your real code
    values: List[ValueNode] = field(default_factory=list)
    states: List[StateNode] = field(default_factory=list)
