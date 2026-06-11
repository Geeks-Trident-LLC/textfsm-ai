# tests/unit/dsl/test_render_literal_text.py


from textfsm_ai.dsl.dsl_renderer import (
    TOKEN_RE,
    render_literal_text,
)


def test_token_re_basic_spacing_and_words():
    text = "abc   xyz"
    tokens = TOKEN_RE.findall(text)
    assert tokens == ["abc", "   ", "xyz"]


def test_token_re_punct_cluster():
    text = ". . . ."
    tokens = TOKEN_RE.findall(text)
    assert tokens == [".", " ", ".", " ", ".", " ", "."]


def test_token_re_mixed_sequence():
    text = "abc  . .  xyz"
    tokens = TOKEN_RE.findall(text)
    assert tokens == ["abc", "  ", ".", " ", ".", "  ", "xyz"]


def test_render_literal_text_digits():
    text = "123"
    out = render_literal_text(text)
    assert out == "digits()"


def test_render_literal_text_word_literal():
    text = "abc"
    out = render_literal_text(text)
    # literal-safe → literal node
    assert out == "abc"


def test_render_literal_text_word_with_number_generalized():
    text = "abc1"
    out = render_literal_text(text)
    # contains number → generalized word()
    assert out == "word()"


def test_render_literal_text_mixed_word_literal_safe():
    text = "connection:"
    out = render_literal_text(text)
    # no digits, safe literal → literal node
    assert out == "connection:"


def test_render_literal_text_mixed_word_generalized():
    text = "connection*"
    out = render_literal_text(text)
    # unsafe literal → mixed-word()
    assert out == "connection*"


def test_render_literal_text_punct_literal():
    text = ":"
    out = render_literal_text(text)
    assert out == ":"


def test_render_literal_text_puncts_literal():
    text = "***"
    out = render_literal_text(text)
    assert out == "***"


def test_render_literal_text_full_example_1():
    text = "abc   xyz   123 connection:"
    out = render_literal_text(text)
    assert out == "abc   xyz   digits() connection:"


def test_render_literal_text_full_example_2():
    text = "abc   var_v1   123 connection:"
    out = render_literal_text(text)
    assert out == "abc   word()   digits() connection:"


def test_render_literal_text_full_example_3():
    text = "abc   xyz   123 connection*"
    out = render_literal_text(text)
    assert out == "abc   xyz   digits() connection*"
