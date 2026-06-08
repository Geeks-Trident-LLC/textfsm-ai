# textfsm_ai/dsl/ast.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KeywordCall:
    name: str
    varname: Optional[str] = None


@dataclass
class SequenceExpression:
    items: List[KeywordCall]
