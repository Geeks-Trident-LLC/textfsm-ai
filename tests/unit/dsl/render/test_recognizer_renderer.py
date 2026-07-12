import textwrap

from textfsm_ai.dsl.ast.parser import parse_textfsm
from textfsm_ai.dsl.engine.render.recognizer import render_recognizer


def test_render_recognizer_single_state():
    template = textwrap.dedent(
        r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """
    ).strip()

    expected = ["^foo\\s+[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*"]

    records = [{"v1": "abc"}]

    ast = parse_textfsm(template, records)
    out = render_recognizer(ast)
    assert out == expected


def test_render_recognizer_multiple_states():

    template = textwrap.dedent(
        r"""
        Value Required v1 (\S+)
        Value v2 (\S+)
        Value Filldown,Fillup v3 (\S+)

        Start
          ^foo ${v1} -> Next
          ^bar ${v2} -> Continue.Record Table

        Table
          ^foobar ${v3} -> Start
    """
    ).strip()

    expected = [
        "^foo\\s+[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*",
        "^bar\\s+[0-9]+",
        "^foobar\\s+(?:[0-9]+\\.[0-9]+|[0-9]+\\.|\\.[0-9]+|[0-9]+)",
    ]

    records = [{"v1": "abc", "v2": "12", "v3": "1.1"}]

    ast = parse_textfsm(template, records)
    out = render_recognizer(ast)
    assert out == expected
