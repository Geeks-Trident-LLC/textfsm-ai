# textfsm_ai/delivery/format/json.py

from dataclasses import asdict
from typing import Any, Dict

from ..core.modes import DeliveryMode
from ..core.package import DeliveryPackage


def _strip_none(obj: Any) -> Any:
    """Recursively remove None values from dataclass dicts."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj


def delivery_to_json_dict(pkg: DeliveryPackage) -> Dict[str, Any]:
    """
    Convert DeliveryPackage to a JSON-safe dict:
    - remove None fields
    - remove empty debug sections
    - ensure mode-aware output
    """
    raw = asdict(pkg)

    # Remove debug section entirely if mode != DEBUG
    if pkg.mode != DeliveryMode.DEBUG:
        raw.pop("debug", None)

    # Remove usage if mode < INFO
    if pkg.mode < DeliveryMode.INFO:
        raw.pop("usage", None)

    # Remove general + explanation if mode < DEFAULT
    if pkg.mode < DeliveryMode.DEFAULT:
        raw.pop("general", None)
        raw.pop("explanation", None)

    # Strip None values recursively
    return _strip_none(raw)
