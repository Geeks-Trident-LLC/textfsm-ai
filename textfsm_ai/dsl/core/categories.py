# textfsm_ai/dsl/categories.py

from enum import Enum, auto


class BaseCategory(Enum):
    # whitespace categories
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
