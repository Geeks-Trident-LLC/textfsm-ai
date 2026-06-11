# textfsm_ai/dsl/aliases.py

from .categories import BaseCategory

ALIASES = {
    "whitespace": BaseCategory.WS,
    "whitespaces": BaseCategory.WS,
    "ws": BaseCategory.WS,
    "wss": BaseCategory.WS,
    "punct": BaseCategory.PUNCT,
    "puncts": BaseCategory.PUNCT,
    "puncts-item": BaseCategory.PUNCT,
    "puncts-group": BaseCategory.PUNCT,
    "digit": BaseCategory.DIGIT,
    "digits": BaseCategory.DIGIT,
    "number": BaseCategory.NUMBER,
    "mixed-number": BaseCategory.MIXED_NUMBER,
    "letter": BaseCategory.LETTER,
    "alnum": BaseCategory.ALNUM,
    "word": BaseCategory.WORD,
    "words": BaseCategory.WORD,
    "mixed-word": BaseCategory.MIXED_WORD,
    "mixed-words": BaseCategory.MIXED_WORD,
    "non-ws": BaseCategory.NON_WS,
    "non-wss": BaseCategory.NON_WS,
    "non-wss-item": BaseCategory.NON_WS,
    "non-wss-group": BaseCategory.NON_WS,
}
