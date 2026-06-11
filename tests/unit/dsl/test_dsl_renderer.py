# tests/unit/dsl/test_dsl_renderer.py

import textwrap

from textfsm_ai.dsl.dsl_renderer import render_dsl
from textfsm_ai.dsl.dsl_reverse import human_dsl_to_machine_dsl


def _strip(s: str) -> str:
    return textwrap.dedent(s).strip()


def test_basic_dsl_render():
    dsl = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {
                        "pattern": r"^abc\s+\. \. \. \. \.\s+123\s+connection:",
                        "action": None,
                    },
                    {
                        "pattern": r"^interface\s+${interface}",
                        "action": "Continue.Record",
                    },
                    {
                        "pattern": r"^\s+mtu\s+${mtu}",
                        "action": None,
                    },
                ],
            }
        ],
        "variables": [
            {
                "name": "interface",
                "keyword": "mixed-word",
                "category": "MIXED_WORD",
                "options": "",
                "expression": "mixed-word(var-interface)",
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

    template = _strip("""
        Value interface ([!-~]*[0-9A-Za-z][!-~]*)
        Value mtu ([0-9]+)
        Start
          ^abc\\s+. \\. \\. \\. \\.\\s+123\\s+connection:
          ^interface\\s+${interface} -> Continue.Record
          ^\\s+mtu\\s+${mtu}
        """)

    sample = _strip("""
        abc   . . . . .   123 connection:
        interface    Ethernet1
          mtu 1500
        """)

    out = render_dsl(dsl, template, sample)

    assert "Start" in out
    assert "mixed-word(var-interface)" in out
    assert "digits(var-mtu)" in out


def test_render_literal_end():
    dsl = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {"pattern": "^foo$$", "action": None},
                ],
            }
        ],
        "variables": [],
    }
    sample = "foo"
    out = render_dsl(dsl, "", sample)
    assert out.strip().endswith("foo end()")


def test_render_variable_end():
    dsl = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {"pattern": "^interface\\s+${interface}$$", "action": None},
                ],
            }
        ],
        "variables": [
            {
                "name": "interface",
                "keyword": "mixed-word",
                "category": "MIXED_WORD",
                "options": "",
                "expression": "mixed-word(var-interface)",
                "expression_regex": "[!-~]*[0-9A-Za-z][!-~]*",
            }
        ],
    }
    sample = "interface Gi0/1"
    out = render_dsl(dsl, "", sample)
    assert out.strip().endswith("mixed-word(var-interface) end()")


def test_roundtrip_end():
    machine1 = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {"pattern": "^foo$$", "action": None},
                    {
                        "pattern": "^interface\\s+${interface}$$",
                        "action": "Continue.Record",
                    },
                ],
            }
        ],
        "variables": [
            {
                "name": "interface",
                "keyword": "mixed-word",
                "category": "MIXED_WORD",
                "options": "",
                "expression": "mixed-word(var-interface)",
                "expression_regex": "[!-~]*[0-9A-Za-z][!-~]*",
            }
        ],
    }

    sample = "foo\ninterface Gi0/1"

    human = render_dsl(machine1, "", sample)
    machine2 = human_dsl_to_machine_dsl(human)

    assert (
        machine1["states"][0]["transitions"][0]["pattern"]
        == machine2["states"][0]["transitions"][0]["pattern"]
    )
    assert (
        machine1["states"][0]["transitions"][1]["pattern"]
        == machine2["states"][0]["transitions"][1]["pattern"]
    )
