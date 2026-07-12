# textfsm_ai/core/models.py

from dataclasses import dataclass
from typing import Any, Optional

from .serializable import Serializable


@dataclass(frozen=True)
class ValidationResult(Serializable):
    data: Optional[Any] = None
    args: Optional[list] = None
    kwargs: Optional[dict] = None
    reason: str = ""
    ready: bool = False
