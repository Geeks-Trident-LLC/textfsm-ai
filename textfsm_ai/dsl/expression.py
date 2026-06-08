# textfsm_ai/dsl/expression.py

from dataclasses import dataclass
from typing import Optional

from .categories import BaseCategory


@dataclass(frozen=True)
class KeywordExpression:
    base: BaseCategory
    min_count: int
    max_count: Optional[int]
    optional: bool
    is_group: bool
    varname: Optional[str] = None
