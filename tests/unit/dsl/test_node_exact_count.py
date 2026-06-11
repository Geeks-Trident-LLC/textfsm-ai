# tests/unit/dsl/test_node_exact_count.py

from textfsm_ai.dsl.nodes import ExactCountNode, create_node

WORD = "[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"
WSS = r"\s+"


def test_exact_0_word():
    node = ExactCountNode(create_node("word"), 0)
    assert node.to_regex() == ""


def test_exact_1_word():
    node = ExactCountNode(create_node("word"), 1)
    assert node.to_regex() == WORD


def test_exact_3_word():
    node = ExactCountNode(create_node("word"), 3)
    # WORD_ITEM = HEAD (?:<wss> HEAD)*
    # exact-3-word = HEAD (?:<wss> HEAD){2}
    assert node.to_regex() == f"{WORD}(?:{WSS}{WORD}){{2}}"


def test_exact_1_word_item():
    node = ExactCountNode(create_node("word-item"), 1)
    assert node.to_regex() == WORD


def test_exact_2_word_item():
    node = ExactCountNode(create_node("word-item"), 2)
    assert node.to_regex() == f"{WORD}(?:{WSS}{WORD}){{1}}"


def test_exact_1_word_group():
    node = ExactCountNode(create_node("word-group"), 1)
    assert node.to_regex() == f"{WORD}(?:{WSS}{WORD})+"


def test_exact_2_word_group():
    node = ExactCountNode(create_node("word-group"), 2)
    WORD_GROUP = f"{WORD}(?:{WSS}{WORD})+"
    assert node.to_regex() == f"{WORD_GROUP}(?:{WSS}{WORD_GROUP}){{1}}"


def test_exact_atomic():
    node = ExactCountNode(create_node("digit"), 4)
    assert node.to_regex() == "[0-9]{4}"


def test_exact_atomic_plus():
    node = ExactCountNode(create_node("digits"), 3)
    assert node.to_regex() == "[0-9]{3}"
