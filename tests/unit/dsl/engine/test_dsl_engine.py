# tests/unit/dsl/engine/test_dsl_engine.py

import textwrap

from textfsm_ai.dsl.engine.dsl_engine import run


def test_run():
    llm_template = textwrap.dedent(
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

    records = [{"v1": "abc", "v2": "12", "v3": "1.1"}]
    result = run(llm_template, records)
    assert result.ready
    assert (
        result.canonical
        == textwrap.dedent(
            r"""
        Value Required v1 ([A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*)
        Value v2 ([0-9]+)
        Value Filldown,Fillup v3 ((?:[0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+|[0-9]+))

        Start
          ^foo\s+${v1} -> Next
          ^bar\s+${v2} -> Continue.Record Table

        Table
          ^foobar\s+${v3} -> Start
        """
        ).strip()
    )

    assert (
        result.readable
        == textwrap.dedent(
            """
        state Start:
          start() foo word(var-v1, options-Required) -> Next
          start() bar digits(var-v2) -> Continue.Record(Table)

        state Table:
          start() foobar number(var-v3, options-Filldown,Fillup) -> Start
        """
        ).strip()
    )

    assert result.recognizers == [
        r"^foo\s+[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*",
        r"^bar\s+[0-9]+",
        r"^foobar\s+(?:[0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+|[0-9]+)",
    ]
