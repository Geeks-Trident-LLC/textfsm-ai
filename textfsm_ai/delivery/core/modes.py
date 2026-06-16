# textfsm_ai/delivery/core/modes.py

from enum import IntEnum


class DeliveryMode(IntEnum):
    QUIET = 0
    DEFAULT = 1
    INFO = 2
    DEBUG = 3

    @classmethod
    def from_str(cls, value: str) -> "DeliveryMode":
        value = value.lower()
        mapping = {
            "quiet": cls.QUIET,
            "default": cls.DEFAULT,
            "info": cls.INFO,
            "debug": cls.DEBUG,
        }
        if value not in mapping:
            raise ValueError(f"Invalid delivery mode: {value}")
        return mapping[value]

    def is_at_least(self, other: "DeliveryMode") -> bool:
        return self.value >= other.value
