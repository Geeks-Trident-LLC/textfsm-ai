# textfsm_ai/dsl/patterns.py

from collections import OrderedDict

from .categories import BaseCategory

# ------------------------------------------------------------
# Primitive building blocks (DSL-visible)
# ------------------------------------------------------------
DIGIT = r"[0-9]"
DIGITS = r"[0-9]+"
LETTER = r"[A-Za-z]"
ALNUM = r"[0-9A-Za-z]"
PUNCT = r"[!-/:-@\[-`{-~]"
PUNCTS = f"{PUNCT}+"
NON_WS = r"\S"
NON_WSS = r"\S+"

# ------------------------------------------------------------
# Higher-level semantic primitives (DSL-visible)
# ------------------------------------------------------------

# number: 123, 0.1, .1, 1.
NUMBER = (
    r"(?:"
    r"[0-9]+\.[0-9]+"  # 1.23
    r"|"
    r"[0-9]+\."  # 1.
    r"|"
    r"\.[0-9]+"  # .1
    r"|"
    r"[0-9]+"  # 123
    r")"
)

# mixed-number: signed, comma-grouped, parenthesized
MIXED_NUMBER = (
    r"(?:"
    r"[+-]?"
    r"(?:\([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?\)"
    r"|"
    r"[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?"
    r")"
    r")"
)

# word: must contain at least one letter
WORD = r"[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"

# mixed-word: must contain at least one alnum, rest can be graph chars
MIXED_WORD = r"[!-~]*[0-9A-Za-z][!-~]*"

# ------------------------------------------------------------
# Ordered patterns (most specific → more general)
# ------------------------------------------------------------

PATTERNS_MAPPING = OrderedDict(
    [
        # single-char primitives
        ("letter", LETTER),
        ("digit", DIGIT),
        ("alnum", ALNUM),
        ("punct", PUNCT),
        ("non-ws", NON_WS),
        # multi-char primitives
        ("digits", DIGITS),
        ("number", NUMBER),
        # mixed-number MUST precede mixed-word
        ("mixed-number", MIXED_NUMBER),
        ("puncts", PUNCTS),
        ("word", WORD),
        # mixed-word AFTER mixed-number
        ("mixed-word", MIXED_WORD),
        ("non-wss", NON_WSS),
        # plural / item / group variants
        ("word-group", f"{WORD}(?:\\s+{WORD})+"),
        ("words", f"{WORD}(?:\\s+{WORD})*"),
        ("word-item", f"{WORD}(?:\\s+{WORD})*"),
        ("mixed-number-group", f"{MIXED_NUMBER}(?:\\s+{MIXED_NUMBER})+"),
        ("mixed-numbers", f"{MIXED_NUMBER}(?:\\s+{MIXED_NUMBER})*"),
        ("mixed-number-item", f"{MIXED_NUMBER}(?:\\s+{MIXED_NUMBER})*"),
        ("mixed-word-group", f"{MIXED_WORD}(?:\\s+{MIXED_WORD})+"),
        ("mixed-words", f"{MIXED_WORD}(?:\\s+{MIXED_WORD})*"),
        ("mixed-word-item", f"{MIXED_WORD}(?:\\s+{MIXED_WORD})*"),
        ("puncts-group", f"{PUNCTS}(?:\\s+{PUNCTS})+"),
        ("puncts-item", f"{PUNCTS}(?:\\s+{PUNCTS})*"),
        ("non-wss-group", f"{NON_WSS}(?:\\s+{NON_WSS})+"),
        ("non-wss-item", f"{NON_WSS}(?:\\s+{NON_WSS})*"),
    ]
)

# ------------------------------------------------------------
# Map keyword → BaseCategory (DSL-visible only)
# ------------------------------------------------------------

KEYWORD_TO_BASE = {
    "letter": BaseCategory.LETTER,
    "digit": BaseCategory.DIGIT,
    "digits": BaseCategory.DIGIT,
    "alnum": BaseCategory.ALNUM,
    "punct": BaseCategory.PUNCT,
    "puncts": BaseCategory.PUNCT,
    "puncts-item": BaseCategory.PUNCT,
    "puncts-group": BaseCategory.PUNCT,
    "non-ws": BaseCategory.NON_WS,
    "non-wss": BaseCategory.NON_WS,
    "non-wss-item": BaseCategory.NON_WS,
    "non-wss-group": BaseCategory.NON_WS,
    "number": BaseCategory.NUMBER,
    "mixed-number": BaseCategory.MIXED_NUMBER,
    "mixed-numbers": BaseCategory.MIXED_NUMBER,
    "mixed-number-item": BaseCategory.MIXED_NUMBER,
    "mixed-number-group": BaseCategory.MIXED_NUMBER,
    "word": BaseCategory.WORD,
    "words": BaseCategory.WORD,
    "word-item": BaseCategory.WORD,
    "word-group": BaseCategory.WORD,
    "mixed-word": BaseCategory.MIXED_WORD,
    "mixed-words": BaseCategory.MIXED_WORD,
    "mixed-word-item": BaseCategory.MIXED_WORD,
    "mixed-word-group": BaseCategory.MIXED_WORD,
}


class Pattern:
    def __init__(self, name: str, regex: str):
        self.name = name
        self.regex = regex


PATTERNS = {key: Pattern(key, pat) for key, pat in PATTERNS_MAPPING.items()}
