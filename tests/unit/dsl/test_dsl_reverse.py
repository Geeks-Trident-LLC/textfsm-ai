# tests/unit/dsl/test_human_dsl_reverse.py

import textwrap

import pytest

from textfsm_ai.dsl.dsl_reverse import (
    human_dsl_to_machine_dsl,
    parse_keyword_call,
    tokenize_human_dsl_body,
)


def _strip(s: str) -> str:
    return textwrap.dedent(s).strip()


# ------------------------------------------------------------
# Tokenizer
# ------------------------------------------------------------


def test_tokenize_human_dsl_body_basic():
    body = "abc   . . . . .   digits() connection:"
    tokens = tokenize_human_dsl_body(body)
    # ensure whitespace preserved and keyword call is atomic
    assert "abc" in tokens
    assert "digits()" in tokens
    assert "connection:" in tokens
    assert any(t.isspace() for t in tokens)


def test_tokenize_human_dsl_body_keyword_with_options():
    body = "interface mixed-word(var-interface, options-Required,List)"
    tokens = tokenize_human_dsl_body(body)
    assert tokens == [
        "interface",
        " ",
        "mixed-word(var-interface, options-Required,List)",
    ]


# ------------------------------------------------------------
# KeywordCall parsing
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "token, expected",
    [
        ("digits()", ("digits", None, "")),
        ("mixed-word()", ("mixed-word", None, "")),
        ("mixed-word(var-interface)", ("mixed-word", "interface", "")),
        (
            "mixed-word(var-interface, options-List)",
            ("mixed-word", "interface", "List"),
        ),
        (
            "mixed-word(var-interface, options-Required,List)",
            ("mixed-word", "interface", "Required,List"),
        ),
    ],
)
def test_parse_keyword_call(token, expected):
    assert parse_keyword_call(token) == expected


# ------------------------------------------------------------
# Variable extraction + options
# ------------------------------------------------------------


def test_variable_extraction_with_options():
    human = _strip("""
        Start
          start() interface mixed-word(var-interface, options-Required,List)
        """)

    dsl = human_dsl_to_machine_dsl(human)
    vars_ = {v["name"]: v for v in dsl["variables"]}

    assert "interface" in vars_
    v = vars_["interface"]

    assert v["keyword"] == "mixed-word"
    assert v["category"] == "MIXED_WORD"
    assert v["options"] == "Required,List"
    assert v["expression"] == "mixed-word(var-interface, options-Required,List)"
    assert "expression_regex" in v


def test_variable_extraction_without_options():
    human = _strip("""
        Start
          start() mtu digits(var-mtu)
        """)

    dsl = human_dsl_to_machine_dsl(human)
    vars_ = {v["name"]: v for v in dsl["variables"]}

    assert "mtu" in vars_
    v = vars_["mtu"]

    assert v["keyword"] == "digits"
    assert v["options"] == ""


# ------------------------------------------------------------
# Pattern generation
# ------------------------------------------------------------


def test_pattern_generation_with_options():
    human = _strip("""
        Start
          start() interface mixed-word(var-interface, options-Required,List)
        """)

    dsl = human_dsl_to_machine_dsl(human)
    t = dsl["states"][0]["transitions"][0]

    assert t["pattern"] == "^interface\\s+${interface}"


def test_pattern_generation_literal_and_keyword():
    human = _strip("""
        Start
          start() abc   . . . . .   digits() connection:
        """)

    dsl = human_dsl_to_machine_dsl(human)
    t = dsl["states"][0]["transitions"][0]

    assert t["pattern"].startswith("^abc")
    assert "connection:" in t["pattern"]
    assert "[0-9]+" in t["pattern"]


# ------------------------------------------------------------
# Action extraction
# ------------------------------------------------------------


def test_action_extraction():
    human = _strip("""
        Start
          start() interface mixed-word(var-interface) -> Continue.Record
        """)

    dsl = human_dsl_to_machine_dsl(human)
    t = dsl["states"][0]["transitions"][0]

    assert t["action"] == "Continue.Record"


# ------------------------------------------------------------
# Multiple transitions + ordering
# ------------------------------------------------------------


def test_multiple_transitions_order_preserved():
    human = _strip("""
        Start
          start() a digits()
          start() b digits()
          start() c digits()
        """)

    dsl = human_dsl_to_machine_dsl(human)
    transitions = dsl["states"][0]["transitions"]

    assert len(transitions) == 3
    assert transitions[0]["pattern"].startswith("^a")
    assert transitions[1]["pattern"].startswith("^b")
    assert transitions[2]["pattern"].startswith("^c")


# ------------------------------------------------------------
# Round-trip stability (machine → human → machine) with options
# ------------------------------------------------------------


def test_roundtrip_machine_human_machine_with_options():
    machine1 = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {
                        "pattern": "^interface\\s+${interface}",
                        "action": "Continue.Record",
                    },
                    {"pattern": "^mtu\\s+${mtu}", "action": None},
                ],
            }
        ],
        "variables": [
            {
                "name": "interface",
                "keyword": "mixed-word",
                "category": "MIXED_WORD",
                "options": "Required,List",
                "expression": "mixed-word(var-interface, options-Required,List)",
                "expression_regex": "[!-~]*[0-9A-Za-z][!-~]*",
            },
            {
                "name": "mtu",
                "keyword": "digits",
                "category": "DIGIT",
                "options": "",
                "expression": "digits(var-mtu)",
                "expression_regex": "[0-9]+",
            },
        ],
    }

    # FIX: sample must match BOTH transitions
    sample = "interface Gi0/1\nmtu 1500"

    from textfsm_ai.dsl.dsl_renderer import render_dsl

    human = render_dsl(machine1, "", sample)

    machine2 = human_dsl_to_machine_dsl(human)

    # Compare state counts
    assert len(machine1["states"]) == len(machine2["states"])

    # Compare transition counts
    assert len(machine1["states"][0]["transitions"]) == len(
        machine2["states"][0]["transitions"]
    )

    # Compare variable keyword + options
    vars1 = {v["name"]: (v["keyword"], v["options"]) for v in machine1["variables"]}
    vars2 = {v["name"]: (v["keyword"], v["options"]) for v in machine2["variables"]}

    assert vars1 == vars2
