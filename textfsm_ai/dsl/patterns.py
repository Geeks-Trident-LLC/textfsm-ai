# textfsm_ai/dsl/patterns.py

from collections import OrderedDict

from .categories import BaseCategory

# ------------------------------------------------------------
# Primitive building blocks
# ------------------------------------------------------------
SPACE = " "
SPACES = " +"
WS = r"\s"
WSS = r"\s+"
DIGIT = r"[0-9]"
DIGITS = r"[0-9]+"
LETTER = r"[A-Za-z]"
ALNUM = r"[0-9A-Za-z]"
PUNCT = r"[!-/:-@\[-`{-~]"
PUNCTS = f"{PUNCT}+"
NON_WS = r"\S"
NON_WSS = r"\S+"
DOT = r"."
DOTS = r".+"

# ------------------------------------------------------------
# Higher-level semantic primitives
# ------------------------------------------------------------

# number: 123, 0.1, .1, 1.
NUMBER = (
    r"(?:"
    r"\d+\.\d+"  # 1.23
    r"|"
    r"\d+\."  # 1.
    r"|"
    r"\.\d+"  # .1
    r"|"
    r"\d+"  # 123
    r")"
)

MIXED_NUMBER = (
    r"(?:"
    r"[+-]?"  # optional sign
    r"(?:\(\d{1,3}(?:,\d{3})*(?:\.\d+)?\)"  # (1,234.56)
    r"|"
    r"\d{1,3}(?:,\d{3})*(?:\.\d+)?"  # 1,234.56
    r")"
    r")"
)


# word: must contain at least one letter
WORD = r"(?=.*[A-Za-z])[0-9A-Za-z_]+"

# mixed-word: must contain at least one alnum, rest can be graph chars (IPv4 or IPv6)
# graph = [!-~] = all visible ASCII except space
MIXED_WORD = r"(?=.*[0-9A-Za-z])[!-~]+"

# ------------------------------------------------------------
# Ordered patterns (most specific → more general)
# ------------------------------------------------------------

PATTERNS_MAPPING = OrderedDict(
    [
        # whitespace
        ("space", SPACE),
        ("ws", WS),
        ("whitespace", WS),
        ("spaces", SPACES),
        ("wss", WSS),
        ("whitespaces", WSS),
        # single-char primitives
        ("letter", LETTER),
        ("digit", DIGIT),
        ("alnum", ALNUM),
        ("punct", PUNCT),
        ("non-ws", NON_WS),
        ("dot", DOT),
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
        ("word-group", f"{WORD}(?:{WS}+{WORD})+"),
        ("words", f"{WORD}(?:{WS}+{WORD})*"),
        ("word-item", f"{WORD}(?:{WS}+{WORD})*"),
        ("mixed-number-group", f"{MIXED_NUMBER}(?:{WS}+{MIXED_NUMBER})+"),
        ("mixed-numbers", f"{MIXED_NUMBER}(?:{WS}+{MIXED_NUMBER})*"),
        ("mixed-number-item", f"{MIXED_NUMBER}(?:{WS}+{MIXED_NUMBER})*"),
        ("mixed-word-group", f"{MIXED_WORD}(?:{WS}+{MIXED_WORD})+"),
        ("mixed-words", f"{MIXED_WORD}(?:{WS}+{MIXED_WORD})*"),
        ("mixed-word-item", f"{MIXED_WORD}(?:{WS}+{MIXED_WORD})*"),
        ("puncts-group", f"{PUNCTS}(?:{WS}+{PUNCTS})+"),
        ("puncts-item", f"{PUNCTS}(?:{WS}+{PUNCTS})*"),
        ("non-wss-group", f"{NON_WSS}(?:{WS}+{NON_WSS})+"),
        ("non-wss-item", f"{NON_WSS}(?:{WS}+{NON_WSS})*"),
        ("dots", DOTS),
    ]
)

# ------------------------------------------------------------
# Map keyword → BaseCategory
# ------------------------------------------------------------

KEYWORD_TO_BASE = {
    # whitespace
    "space": BaseCategory.SPACE,
    "whitespace": BaseCategory.WS,
    "spaces": BaseCategory.WS,
    "whitespaces": BaseCategory.WS,
    "ws": BaseCategory.WS,
    "wss": BaseCategory.WS,
    # letter
    "letter": BaseCategory.LETTER,
    # digit
    "digit": BaseCategory.DIGIT,
    "digits": BaseCategory.DIGIT,
    # alnum
    "alnum": BaseCategory.ALNUM,
    # punct
    "punct": BaseCategory.PUNCT,
    "puncts": BaseCategory.PUNCT,
    "puncts-item": BaseCategory.PUNCT,
    "puncts-group": BaseCategory.PUNCT,
    # non-ws
    "non-ws": BaseCategory.NON_WS,
    "non-wss": BaseCategory.NON_WS,
    "non-wss-item": BaseCategory.NON_WS,
    "non-wss-group": BaseCategory.NON_WS,
    # dot
    "dot": BaseCategory.DOT,
    "dots": BaseCategory.DOT,
    # number
    "number": BaseCategory.NUMBER,
    # mixed-number
    "mixed-number": BaseCategory.MIXED_NUMBER,
    "mixed-numbers": BaseCategory.MIXED_NUMBER,
    "mixed-number-item": BaseCategory.MIXED_NUMBER,
    "mixed-number-group": BaseCategory.MIXED_NUMBER,
    # word
    "word": BaseCategory.WORD,
    "words": BaseCategory.WORD,
    "word-item": BaseCategory.WORD,
    "word-group": BaseCategory.WORD,
    # mixed-word
    "mixed-word": BaseCategory.MIXED_WORD,
    "mixed-words": BaseCategory.MIXED_WORD,
    "mixed-word-item": BaseCategory.MIXED_WORD,
    "mixed-word-group": BaseCategory.MIXED_WORD,
}
