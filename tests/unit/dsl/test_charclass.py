# tests/unit/dsl/test_charclass.py

from textfsm_ai.dsl.charclass import is_digit, is_letter, is_non_ws, is_punct, is_space


def test_charclass_space():
    assert is_space(" ")
    assert is_space("\t")
    assert not is_space("a")


def test_charclass_digit():
    assert is_digit("5")
    assert not is_digit("a")


def test_charclass_letter():
    assert is_letter("a")
    assert is_letter("Z")
    assert not is_letter("1")


def test_charclass_punct():
    assert is_punct("-")
    assert is_punct("!")
    assert not is_punct("a")
    assert not is_punct("1")
    assert not is_punct(" ")


def test_charclass_non_ws():
    assert is_non_ws("a")
    assert is_non_ws("1")
    assert is_non_ws("-")
    assert not is_non_ws(" ")
