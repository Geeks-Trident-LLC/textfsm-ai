# tests/unit/dsl/test_tokenclass.py

from textfsm_ai.dsl.tokenclass import (
    token_is_alnum,
    token_is_digit,
    token_is_letter,
    token_is_mixed_number,
    token_is_mixed_word,
    token_is_non_ws,
    token_is_number,
    token_is_punct,
    token_is_space,
    token_is_word,
)


def test_token_space():
    assert token_is_space("   ")
    assert not token_is_space("a")


def test_token_digit():
    assert token_is_digit("123")
    assert not token_is_digit("12a")


def test_token_letter():
    assert token_is_letter("abc")
    assert not token_is_letter("a1")


def test_token_alnum():
    assert token_is_alnum("a1")
    assert not token_is_alnum("a-")


def test_token_punct():
    assert token_is_punct("!!!")
    assert not token_is_punct("a")


def test_token_non_ws():
    assert token_is_non_ws("abc")
    assert not token_is_non_ws(" ")


def test_token_word():
    assert token_is_word("abc")
    assert token_is_word("a_b")
    assert not token_is_word("123")  # must contain letter
    assert not token_is_word("a-b")  # '-' not allowed


def test_token_mixed_word():
    assert token_is_mixed_word("a-b")
    assert token_is_mixed_word("1.2")
    assert not token_is_mixed_word("---")  # must contain alnum


def test_token_number():
    assert token_is_number("123")
    assert token_is_number("1.23")
    assert not token_is_number("1a")


def test_token_mixed_number():
    assert token_is_mixed_number("v1")
    assert token_is_mixed_number("1a")
    assert not token_is_mixed_number("123")  # pure number
    assert not token_is_mixed_number("abc")  # must contain digit
