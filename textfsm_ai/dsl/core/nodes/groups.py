# ------------------------------------------------------------
# Keyword semantic groups
# ------------------------------------------------------------

from enum import Enum, auto

WS = r"\s"
WSS = r"\s+"


class KeywordGroup(Enum):
    ATOMIC = auto()  # digit, letter, alnum, punct, non-ws
    ATOMIC_PLUS = auto()  # digits, puncts, non-wss
    WORDLIKE = auto()  # word, mixed-word, number, mixed-number
    ITEM = auto()  # words, word-item, puncts-item, etc.
    GROUP = auto()  # word-group, mixed-word-group, puncts-group, etc.


CUSTOM_KEYWORD_MAPPING = {
    "char": ".",
    "any": ".*",
    "some": ".+",
    "ws": WS,
    "wss": WSS,
    "whitespace": WS,
    "whitespaces": WSS,
}

KEYWORD_GROUP = {
    # -------------------------
    # atomic-group
    # -------------------------
    "digit": KeywordGroup.ATOMIC,
    "letter": KeywordGroup.ATOMIC,
    "alnum": KeywordGroup.ATOMIC,
    "punct": KeywordGroup.ATOMIC,
    "non-ws": KeywordGroup.ATOMIC,
    "char": KeywordGroup.ATOMIC,
    "ws": KeywordGroup.ATOMIC,
    "whitespace": KeywordGroup.ATOMIC,
    # -------------------------
    # atomic-plus-group
    # -------------------------
    "digits": KeywordGroup.ATOMIC_PLUS,
    "puncts": KeywordGroup.ATOMIC_PLUS,
    "non-wss": KeywordGroup.ATOMIC_PLUS,
    "any": KeywordGroup.ATOMIC_PLUS,
    "some": KeywordGroup.ATOMIC_PLUS,
    "wss": KeywordGroup.ATOMIC_PLUS,
    "whitespaces": KeywordGroup.ATOMIC_PLUS,
    # -------------------------
    # word-like-group
    # -------------------------
    "word": KeywordGroup.WORDLIKE,
    "mixed-word": KeywordGroup.WORDLIKE,
    "number": KeywordGroup.WORDLIKE,
    "mixed-number": KeywordGroup.WORDLIKE,
    # -------------------------
    # item-group
    # <base>(<wss><base>)*
    # -------------------------
    "words": KeywordGroup.ITEM,
    "mixed-words": KeywordGroup.ITEM,
    "numbers": KeywordGroup.ITEM,
    "mixed-numbers": KeywordGroup.ITEM,
    "word-item": KeywordGroup.ITEM,
    "mixed-word-item": KeywordGroup.ITEM,
    "number-item": KeywordGroup.ITEM,
    "mixed-number-item": KeywordGroup.ITEM,
    "puncts-item": KeywordGroup.ITEM,
    "non-wss-item": KeywordGroup.ITEM,
    # -------------------------
    # group-group
    # <base>(<wss><base>)+
    # -------------------------
    "word-group": KeywordGroup.GROUP,
    "mixed-word-group": KeywordGroup.GROUP,
    "number-group": KeywordGroup.GROUP,
    "mixed-number-group": KeywordGroup.GROUP,
    "puncts-group": KeywordGroup.GROUP,
    "non-wss-group": KeywordGroup.GROUP,
}


def keyword_group(name: str) -> KeywordGroup:
    return KEYWORD_GROUP.get(name, KeywordGroup.WORDLIKE)


def base_keyword(name: str) -> str:
    if name.endswith("-group"):
        return name[:-6]  # remove "-group"
    if name.endswith("-item"):
        return name[:-5]  # remove "-item"

    mapping = {
        "words": "word",
        "mixed-words": "mixed-word",
        "numbers": "number",
        "mixed-numbers": "mixed-number",
    }

    return mapping.get(name, name)
