import textwrap

from textfsm_ai.dsl.dsl_renderer import render_dsl


def _strip(s: str) -> str:
    return textwrap.dedent(s).strip()


def test_basic_dsl_render():
    dsl = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {"pattern": r"^abc\s+xyz\s+123\s+connection:", "action": None},
                    {
                        "pattern": "^interface\\s+${interface}",
                        "action": "Continue.Record",
                    },
                    {
                        "pattern": "^\\s+mtu\\s+${mtu}",
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
          ^abc\\s+xyz\\s+123\\s+connection:
          ^interface\\s+${interface} -> Continue.Record
          ^\\s+mtu\\s+${mtu}
        """)

    sample = _strip("""
        abc   xyz   123 connection:
        interface    Ethernet1
          mtu 1500
        """)

    breakpoint()
    out = render_dsl(dsl, template, sample)

    assert "Start" in out
    assert "mixed-word(var-interface)" in out
    assert "digits(var-mtu)" in out
