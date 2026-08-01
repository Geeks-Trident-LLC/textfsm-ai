from enum import Enum
from typing import Dict, List


class Tier(str, Enum):
    QUALITY_CHAT = "quality-chat"
    BALANCE_CHAT = "balance-chat"
    SPEED_CHAT = "speed-chat"
    THINKING_CHAT = "thinking-chat"
    OTHER = "other"


TierGroups = Dict[Tier, List[str]]


def empty_tier_groups() -> TierGroups:
    return {
        Tier.QUALITY_CHAT: [],
        Tier.BALANCE_CHAT: [],
        Tier.SPEED_CHAT: [],
        Tier.THINKING_CHAT: [],
        Tier.OTHER: [],
    }
