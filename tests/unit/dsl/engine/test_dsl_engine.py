# tests/unit/dsl/engine/test_dsl_engine.py

import textwrap
from unittest.mock import patch

from textfsm_ai.dsl.engine.dsl_engine import run

_VALID_TEMPLATE = textwrap.dedent(
    r"""
    Value Required v1 (\S+)

    Start
      ^foo ${v1} -> Record
    """
).strip()
_VALID_RECORDS = [{"v1": "abc"}]


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


def test_run_build_ast_failure():
    with patch(
        "textfsm_ai.dsl.engine.dsl_engine.parse_textfsm",
        side_effect=ValueError("bad template"),
    ):
        result = run("garbage template", [])

    assert result.ready is False
    assert result.name == "build-ast"
    assert "BUILD-AST-ERROR" in result.reason
    assert "ValueError: bad template" in result.reason


def test_run_render_canonical_failure():
    with patch(
        "textfsm_ai.dsl.engine.dsl_engine.render_template",
        side_effect=RuntimeError("canonical boom"),
    ):
        result = run(_VALID_TEMPLATE, _VALID_RECORDS)

    assert result.ready is False
    assert result.name == "render-canonical-template"
    assert "RENDER-CANONICAL-ERROR" in result.reason
    assert "RuntimeError: canonical boom" in result.reason
    assert result.ast is not None


def test_run_render_readable_failure():
    with patch(
        "textfsm_ai.dsl.engine.dsl_engine.render_readable",
        side_effect=RuntimeError("readable boom"),
    ):
        result = run(_VALID_TEMPLATE, _VALID_RECORDS)

    assert result.ready is False
    assert result.name == "render-readable-dsl"
    assert "RENDER-READABLE-ERROR" in result.reason
    assert "RuntimeError: readable boom" in result.reason
    assert result.canonical is not None


def test_run_render_recognizer_failure():
    with patch(
        "textfsm_ai.dsl.engine.dsl_engine.render_recognizer",
        side_effect=RuntimeError("recognizer boom"),
    ):
        result = run(_VALID_TEMPLATE, _VALID_RECORDS)

    assert result.ready is False
    assert result.name == "render-recognizer-patterns"
    assert "RENDER-RECOGNIZER-ERROR" in result.reason
    assert "RuntimeError: recognizer boom" in result.reason
    assert result.readable is not None
