# tests/unit/dsl/test_keyword_call.py

import pytest

from textfsm_ai.dsl.dsl_reverse import parse_keyword_call


@pytest.mark.parametrize(
    "token, expected",
    [
        ("digits()", ("digits", None, "")),
        ("mixed-word()", ("mixed-word", None, "")),
        ("mixed-word(var-x)", ("mixed-word", "x", "")),
        ("mixed-word(var-x, options-List)", ("mixed-word", "x", "List")),
        (
            "mixed-word(var-x, options-Required,List)",
            ("mixed-word", "x", "Required,List"),
        ),
    ],
)
def test_parse_keyword_call(token, expected):
    assert parse_keyword_call(token) == expected
