# tests/unit/dsl/test_dsl_actions.py

from textfsm_ai.dsl.dsl_renderer import render_dsl


def test_action_position():
    dsl = {
        "states": [
            {
                "name": "Start",
                "transitions": [
                    {"pattern": "^foo\\s+${x}$$", "action": "Continue.Record"},
                ],
            }
        ],
        "variables": [
            {
                "name": "x",
                "keyword": "digits",
                "category": "DIGIT",
                "options": "",
                "expression": "digits(var-x)",
                "expression_regex": "[0-9]+",
            }
        ],
    }

    sample = "foo 123"
    human = render_dsl(dsl, "", sample)

    assert human.strip().endswith("digits(var-x) end() -> Continue.Record")
