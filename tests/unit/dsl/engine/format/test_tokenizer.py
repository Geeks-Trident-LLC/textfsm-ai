# tests/unit/dsl/engine/format/test_tokenizer.py

from textfsm_ai.dsl.engine.format.dsl_reverse import tokenize_human_dsl_body


def test_tokenizer_basic():
    body = "abc   def"
    assert tokenize_human_dsl_body(body) == ["abc", "   ", "def"]


def test_tokenizer_keyword_call():
    body = "mixed-word(var-x)"
    assert tokenize_human_dsl_body(body) == ["mixed-word(var-x)"]


def test_tokenizer_keyword_call_with_options():
    body = "mixed-word(var-x, options-Required,List)"
    assert tokenize_human_dsl_body(body) == ["mixed-word(var-x, options-Required,List)"]


def test_tokenizer_nested_parens():
    body = "kw(var-x, options-A,(B,C))"
    assert tokenize_human_dsl_body(body) == ["kw(var-x, options-A,(B,C))"]


def test_tokenizer_literal_punct():
    body = ". . . ."
    assert tokenize_human_dsl_body(body) == [".", " ", ".", " ", ".", " ", "."]


def test_tokenizer_mixed_literal_and_keyword():
    body = "abc mixed-word(var-x) xyz"
    assert tokenize_human_dsl_body(body) == [
        "abc",
        " ",
        "mixed-word(var-x)",
        " ",
        "xyz",
    ]
