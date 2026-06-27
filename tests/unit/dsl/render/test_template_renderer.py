# tests/unit/dsl/render/test_template_renderer.py

import textwrap

from textfsm_ai.dsl.ast.nodes import (
    Action,
)
from textfsm_ai.dsl.ast.parser import parse_textfsm
from textfsm_ai.dsl.engine.render.template import (
    _render_actions,
    _render_pattern,
    render_template,
)

# ------------------------------------------------------------
# Pattern rendering tests
# ------------------------------------------------------------


def test_render_pattern_canonical():
    template = textwrap.dedent(r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """).strip()

    expected = r"^foo\s+${v1}"

    records = [{"v1": "abc"}]

    ast = parse_textfsm(template, records)
    out = _render_pattern(ast.states[0].rules[0].pattern, canonicalized=True)
    assert out == expected


def test_render_pattern_raw():
    template = textwrap.dedent(r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """).strip()

    expected = r"^foo ${v1}"

    records = [{"v1": "abc"}]
    ast = parse_textfsm(template, records)
    out = _render_pattern(ast.states[0].rules[0].pattern, canonicalized=False)
    assert out == expected


# ------------------------------------------------------------
# Action rendering tests
# ------------------------------------------------------------


def test_render_action_line_only():
    a = Action(line_action="Next", record_action=None, state=None)
    assert _render_actions([a]) == "Next"


def test_render_action_line_with_state():
    a = Action(line_action="Next", record_action=None, state="Foo")
    assert _render_actions([a]) == "Next Foo"


def test_render_action_record_only():
    a = Action(line_action=None, record_action="Record", state=None)
    assert _render_actions([a]) == "Record"


def test_render_action_record_with_state():
    a = Action(line_action=None, record_action="Record", state="Foo")
    assert _render_actions([a]) == "Record Foo"


def test_render_action_combined():
    a = Action(line_action="Next", record_action="Record", state=None)
    assert _render_actions([a]) == "Next.Record"


def test_render_action_combined_with_state():
    a = Action(line_action="Next", record_action="Record", state="Foo")
    assert _render_actions([a]) == "Next.Record Foo"


def test_render_action_eof():
    a = Action(eof_action=True)
    assert _render_actions([a]) == "EOF"


def test_render_action_error():
    a = Action(error_pattern="^bad")
    assert _render_actions([a]) == "Error ^bad"


# ------------------------------------------------------------
# Template rendering tests
# ------------------------------------------------------------


def test_render_template_canonical():

    template = textwrap.dedent(r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """).strip()

    expected = textwrap.dedent(r"""
        Value Required v1 ([A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*)

        Start
          ^foo\s+${v1}
    """).strip()

    records = [{"v1": "abc"}]
    ast = parse_textfsm(template, records)
    out = render_template(ast, canonicalized=True)
    assert out == expected


def test_render_template_raw():

    template = textwrap.dedent(r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """).strip()

    expected = textwrap.dedent(r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """).strip()

    records = [{"v1": "abc"}]
    ast = parse_textfsm(template, records)
    out = render_template(ast, canonicalized=False)
    assert out == expected


def test_render_template_multiple_states():

    template = textwrap.dedent(r"""
        Value Required v1 (\S+)
        Value v2 (\S+)
        Value Filldown,Fillup v3 (\S+)

        Start
          ^foo ${v1} -> Next
          ^bar ${v2} -> Continue.Record Table

        Table
          ^foobar ${v3} -> Start
    """).strip()

    expected = textwrap.dedent(r"""
        Value Required v1 ([A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*)
        Value v2 ([0-9]+)
        Value Filldown,Fillup v3 ((?:[0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+|[0-9]+))

        Start
          ^foo\s+${v1} -> Next
          ^bar\s+${v2} -> Continue.Record Table

        Table
          ^foobar\s+${v3} -> Start
    """).strip()

    records = [{"v1": "abc", "v2": "12", "v3": "1.1"}]

    ast = parse_textfsm(template, records)
    out = render_template(ast, canonicalized=True)
    assert out == expected
