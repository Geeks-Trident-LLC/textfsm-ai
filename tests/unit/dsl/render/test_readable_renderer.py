import textwrap

from textfsm_ai.dsl.ast.nodes import (
    Action,
    LiteralNode,
    PatternNode,
)
from textfsm_ai.dsl.ast.parser import parse_textfsm
from textfsm_ai.dsl.engine.render.readable import (
    _render_action_readable,
    _render_pattern_readable,
    render_readable,
)

# ------------------------------------------------------------
# Pattern rendering tests
# ------------------------------------------------------------


def test_render_pattern_readable_simple():

    template = textwrap.dedent(
        r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """
    ).strip()
    expected = "start() foo word(var-v1, options-Required)"
    records = [{"v1": "abc"}]

    ast = parse_textfsm(template, records)

    out = _render_pattern_readable(ast.states[0].rules[0].pattern)
    assert out == expected


def test_render_pattern_readable_literal_only():
    p = PatternNode(
        items=[
            LiteralNode(raw="abc", textfsm_repr="abc", expression="abc", regex="abc")
        ]
    )
    assert _render_pattern_readable(p) == "abc"


# ------------------------------------------------------------
# Action rendering tests
# ------------------------------------------------------------


def test_render_action_readable_line_only():
    a = Action(line_action="Next")
    assert _render_action_readable([a]) == "Next"


def test_render_action_readable_line_with_state():
    a = Action(line_action="Next", state="Foo")
    assert _render_action_readable([a]) == "Next(Foo)"


def test_render_action_readable_record_only():
    a = Action(record_action="Record")
    assert _render_action_readable([a]) == "Record"


def test_render_action_readable_record_with_state():
    a = Action(record_action="Record", state="Foo")
    assert _render_action_readable([a]) == "Record(Foo)"


def test_render_action_readable_combined():
    a = Action(line_action="Next", record_action="Record")
    assert _render_action_readable([a]) == "Next.Record"


def test_render_action_readable_combined_with_state():
    a = Action(line_action="Next", record_action="Record", state="Foo")
    assert _render_action_readable([a]) == "Next.Record(Foo)"


def test_render_action_readable_eof():
    a = Action(eof_action=True)
    assert _render_action_readable([a]) == "EOF"


def test_render_action_readable_error():
    a = Action(error_pattern="^bad$")
    assert _render_action_readable([a]) == "Error(^bad$)"


def test_render_action_readable_state_only():
    a = Action(state="Table")
    assert _render_action_readable([a]) == "Table"


# ------------------------------------------------------------
# Full template rendering tests
# ------------------------------------------------------------


def test_render_readable_single_state():
    template = textwrap.dedent(
        r"""
        Value Required v1 (\S+)

        Start
          ^foo ${v1}
    """
    ).strip()
    expected = textwrap.dedent(
        """
        state Start:
          start() foo word(var-v1, options-Required)
    """
    ).strip()

    records = [{"v1": "abc"}]

    ast = parse_textfsm(template, records)

    out = render_readable(ast)
    assert out == expected


def test_render_readable_multiple_states():

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

    expected = textwrap.dedent(
        r"""
    state Start:
      start() foo word(var-v1, options-Required) -> Next
      start() bar digits(var-v2) -> Continue.Record(Table)

    state Table:
      start() foobar number(var-v3, options-Filldown,Fillup) -> Start
    """
    ).strip()

    records = [{"v1": "abc", "v2": "12", "v3": "1.1"}]

    ast = parse_textfsm(template, records)

    out = render_readable(ast)
    assert out == expected
