# tests/unit/dsl/test_range_quantity_node.py

import re

from textfsm_ai.dsl.nodes import RangeQuantityNode, create_node

WORD = r"[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"
DIGIT = r"[0-9]"
WSS = r"\s+"


def _re(pattern: str):
    return re.compile(f"^{pattern}$")


# ---------- helpers to build nodes ----------


def word_node():
    return create_node("word")


def word_item_node():
    return create_node("word-item")


def word_group_node():
    return create_node("word-group")


def digit_node():
    return create_node("digit")


def digits_node():
    return create_node("digits")


# ---------- lo == hi == 0 ----------


def test_range_0_0_word():
    node = RangeQuantityNode(word_node(), 0, 0)
    assert node.to_regex() == ""


# ---------- lo == hi > 0 (exact count via RangeQuantityNode) ----------


def test_range_3_3_word():
    node = RangeQuantityNode(word_node(), 3, 3)
    pattern = node.to_regex()
    assert pattern == f"{WORD}(?:{WSS}{WORD}){{2}}"
    r = _re(pattern)
    assert r.match("a b c")
    assert not r.match("a b")
    assert not r.match("a b c d")


def test_range_2_2_word_item():
    node = RangeQuantityNode(word_item_node(), 2, 2)
    pattern = node.to_regex()
    assert pattern == f"{WORD}(?:{WSS}{WORD}){{1}}"
    r = _re(pattern)
    assert r.match("a b")
    assert not r.match("a")
    assert not r.match("a b c")


def test_range_1_1_word_group():
    node = RangeQuantityNode(word_group_node(), 1, 1)
    pattern = node.to_regex()
    WORD_GROUP = f"{WORD}(?:{WSS}{WORD})+"
    assert pattern == WORD_GROUP
    r = _re(pattern)
    assert r.match("a b")
    assert r.match("a b c")
    assert not r.match("a")


def test_range_4_4_digit():
    node = RangeQuantityNode(digit_node(), 4, 4)
    assert node.to_regex() == f"{DIGIT}{{4}}"


def test_range_3_3_digits():
    node = RangeQuantityNode(digits_node(), 3, 3)
    # digits = [0-9]+ → base = [0-9]
    assert node.to_regex() == f"{DIGIT}{{3}}"


# ---------- lo = 0, hi = INF ----------


def test_range_0_inf_word():
    node = RangeQuantityNode(word_node(), 0, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")  # 0 words
    assert r.match("a")  # 1 word
    assert r.match("a b c")  # many words


def test_range_0_inf_word_item():
    node = RangeQuantityNode(word_item_node(), 0, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("a")
    assert r.match("a b c")


def test_range_0_inf_word_group():
    node = RangeQuantityNode(word_group_node(), 0, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")  # 0 phrases
    assert r.match("a b")  # 1 phrase
    assert r.match("a b   c d")  # 2 phrases
    assert r.match("a b c   d e f")  # 2 phrases with 3 words each


def test_range_0_inf_digit():
    node = RangeQuantityNode(digit_node(), 0, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("1")
    assert r.match("12345")


def test_range_0_inf_digits():
    node = RangeQuantityNode(digits_node(), 0, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("1")
    assert r.match("12345")


# ---------- lo = 0, hi finite ----------


def test_range_0_2_word():
    node = RangeQuantityNode(word_node(), 0, 2)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")  # 0 words
    assert r.match("a")  # 1 word
    assert r.match("a b")  # 2 words
    assert not r.match("a b c")


def test_range_0_3_word_item():
    node = RangeQuantityNode(word_item_node(), 0, 3)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("a")
    assert r.match("a b")
    assert r.match("a b c")
    assert not r.match("a b c d")


def test_range_0_2_word_group():
    node = RangeQuantityNode(word_group_node(), 0, 2)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")  # 0 phrases
    assert r.match("a b")  # 1 phrase
    assert r.match("a b   c d")  # 2 phrases


def test_range_0_4_digit():
    node = RangeQuantityNode(digit_node(), 0, 4)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("1")
    assert r.match("1234")
    assert not r.match("12345")


def test_range_0_3_digits():
    node = RangeQuantityNode(digits_node(), 0, 3)
    pattern = node.to_regex()
    r = _re(pattern)
    assert r.match("")
    assert r.match("1")
    assert r.match("12")
    assert r.match("123")
    assert not r.match("1234")


# ---------- lo > 0, hi = INF ----------


def test_range_2_inf_word():
    node = RangeQuantityNode(word_node(), 2, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("a")
    assert r.match("a b")
    assert r.match("a b c d")


def test_range_3_inf_word_item():
    node = RangeQuantityNode(word_item_node(), 3, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("a b")
    assert r.match("a b c")
    assert r.match("a b c d e")


def test_range_2_inf_word_group():
    node = RangeQuantityNode(word_group_node(), 2, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("a b")  # 1 phrase
    assert r.match("a b   c d")  # 2 phrases
    assert r.match("a b   c d   e f")  # 3 phrases


def test_range_2_inf_digit():
    node = RangeQuantityNode(digit_node(), 2, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("1")
    assert r.match("12")
    assert r.match("12345")


def test_range_3_inf_digits():
    node = RangeQuantityNode(digits_node(), 3, None)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("12")
    assert r.match("123")
    assert r.match("123456")


# ---------- lo > 0, hi finite ----------


def test_range_2_4_word():
    node = RangeQuantityNode(word_node(), 2, 4)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("a")
    assert r.match("a b")
    assert r.match("a b c")
    assert r.match("a b c d")
    assert not r.match("a b c d e")


def test_range_1_3_word_item():
    node = RangeQuantityNode(word_item_node(), 1, 3)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("")  # need at least 1 word
    assert r.match("a")
    assert r.match("a b")
    assert r.match("a b c")
    assert not r.match("a b c d")


def test_range_2_3_word_group():
    node = RangeQuantityNode(word_group_node(), 2, 3)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("a b")  # 1 phrase
    assert r.match("a b   c d")  # 2 phrases
    assert r.match("a b   c d   e f")  # 3 phrases


def test_range_2_5_digit():
    node = RangeQuantityNode(digit_node(), 2, 5)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("1")
    assert r.match("12")
    assert r.match("12345")
    assert not r.match("123456")


def test_range_1_4_digits():
    node = RangeQuantityNode(digits_node(), 1, 4)
    pattern = node.to_regex()
    r = _re(pattern)
    assert not r.match("")  # need at least 1
    assert r.match("1")
    assert r.match("12")
    assert r.match("1234")
    assert not r.match("12345")
