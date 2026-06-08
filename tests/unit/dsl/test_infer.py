import pytest

from textfsm_ai.dsl.categories import BaseCategory
from textfsm_ai.dsl.infer import infer_base_category, infer_base_keyword


@pytest.mark.parametrize(
    "tokens, expected_keyword, expected_category",
    [
        # word
        (["abc"], "word", BaseCategory.WORD),
        (["xyz"], "word", BaseCategory.WORD),
        (["abc", "xyz"], "word", BaseCategory.WORD),
        # word-group
        (["abc xyz"], "word-group", BaseCategory.WORD),
        # words (multi-token mixed)
        (["abc xyz", "def"], "words", BaseCategory.WORD),
        # number
        (["123"], "digits", BaseCategory.DIGIT),
        (["0.1"], "number", BaseCategory.NUMBER),
        ([".1"], "number", BaseCategory.NUMBER),
        (["1."], "number", BaseCategory.NUMBER),
        # mixed-number
        (["+2.2"], "mixed-number", BaseCategory.MIXED_NUMBER),
        (["(2.2)"], "mixed-number", BaseCategory.MIXED_NUMBER),
        (["1,200.50"], "mixed-number", BaseCategory.MIXED_NUMBER),
        # whitespace
        ([" "], "space", BaseCategory.SPACE),
        (["\t"], "whitespace", BaseCategory.WS),
    ],
)
def test_infer(tokens, expected_keyword, expected_category):
    kw = infer_base_keyword(tokens)
    cat = infer_base_category(tokens)

    if expected_keyword in ("space", "whitespace", "ws"):
        assert kw in ("space", "whitespace", "ws")
    else:
        assert kw == expected_keyword

    assert cat == expected_category
