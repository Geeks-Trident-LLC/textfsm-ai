# tests/unit/dsl/engine/recognizer/test_dsl_recognizer.py

from textfsm_ai.dsl.engine.recognizer.dsl_recognizer import recognize_dsl_patterns


def _sample_dsl():
    return {
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


def _sample_template():
    from textwrap import dedent

    return dedent("""
        Value interface ([!-~]*[0-9A-Za-z][!-~]*)
        Value mtu ([0-9]+)
        Start
          ^abc\\s+. \\. \\. \\. \\.\\s+123\\s+connection:
          ^interface\\s+${interface} -> Continue.Record
          ^\\s+mtu\\s+${mtu}
    """).strip()


def test_recognizer_literal_and_variables_using_dsl():
    dsl = _sample_dsl()
    sample = "abc   . . . . .   123 connection:\ninterface Gi0/1\n  mtu 1500\n"
    result = recognize_dsl_patterns(dsl=dsl, template=None, sample=sample, debug=False)
    lines = result.splitlines()

    # literal recognizer: has markers and generalized middle
    assert any(line.startswith("^abc") and "connection:" in line for line in lines)
    assert any("123" not in line and "[0-9]+" in line for line in lines)

    # variable recognizers
    assert "^interface\\s+" in result
    assert "[!-~]*[0-9A-Za-z][!-~]*" in result
    assert "^\\s+mtu\\s+[0-9]+" in result


def test_recognizer_literal_and_variables_using_template():
    template = _sample_template()
    sample = "abc   . . . . .   123 connection:\ninterface Gi0/1\n  mtu 1500\n"
    result = recognize_dsl_patterns(
        dsl=None, template=template, sample=sample, debug=False
    )
    lines = result.splitlines()

    # literal recognizer: has markers and generalized middle
    assert any(line.startswith("^abc") and "connection:" in line for line in lines)
    assert any("123" not in line and "[0-9]+" in line for line in lines)

    # variable recognizers
    assert "^interface\\s+" in result
    assert "[!-~]*[0-9A-Za-z][!-~]*" in result
    assert "^\\s+mtu\\s+[0-9]+" in result
