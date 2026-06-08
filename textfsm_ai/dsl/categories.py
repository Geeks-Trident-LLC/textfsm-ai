# textfsm_ai/dsl/categories.py

from enum import Enum, auto


class BaseCategory(Enum):
    DOT = auto()

    # whitespace categories
    SPACE = auto()  # literal " "
    WS = auto()  # general whitespace: \s, \s+

    # punctuation
    PUNCT = auto()

    # digits / numbers
    DIGIT = auto()
    NUMBER = auto()
    MIXED_NUMBER = auto()

    # letters / alnum / words
    LETTER = auto()
    ALNUM = auto()
    WORD = auto()
    MIXED_WORD = auto()

    # non-whitespace
    NON_WS = auto()


# ------------------------------------------------------------
# Specificity order (most specific → most general)
# ------------------------------------------------------------
SPECIFICITY_ORDER = [
    BaseCategory.LETTER,  # single letter
    BaseCategory.DIGIT,  # single digit
    BaseCategory.NUMBER,  # pure number
    BaseCategory.MIXED_NUMBER,  # number+non-digit
    BaseCategory.ALNUM,  # single alnum
    BaseCategory.WORD,  # pure word
    BaseCategory.MIXED_WORD,  # word+punct (IPv4/IPv6/etc)
    BaseCategory.PUNCT,  # punctuation-only tokens
    BaseCategory.SPACE,  # literal " "
    BaseCategory.WS,  # general whitespace (\t, \n, etc)
    BaseCategory.NON_WS,  # any non-whitespace
    BaseCategory.DOT,  # catch-all
]
