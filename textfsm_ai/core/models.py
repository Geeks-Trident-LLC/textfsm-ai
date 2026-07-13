# textfsm_ai/core/models.py

from dataclasses import dataclass
from typing import Any, Optional

from .serializable import Serializable


@dataclass(frozen=True)
class ValidationResult(Serializable):
    """Generic pass/fail validation outcome.

    Attributes:
        data: The value that was validated (e.g. the template string, for
            `validate_template()`).
        args: Reserved for callers that validate against positional inputs;
            unused by `validate_template()`.
        kwargs: Reserved for callers that validate against keyword inputs;
            unused by `validate_template()`.
        reason: Failure reason if `ready` is False; "" on success.
        ready: True if validation succeeded.
    """

    data: Optional[Any] = None
    args: Optional[list] = None
    kwargs: Optional[dict] = None
    reason: str = ""
    ready: bool = False
