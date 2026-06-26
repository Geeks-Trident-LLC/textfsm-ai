import pytest

from textfsm_ai.dsl.ast.nodes import Action, RuleNode, TemplateAST, ValueNode, VarNode
from textfsm_ai.dsl.ast.parser import (
    parse_action_expr,
    parse_rule_line,
    parse_textfsm,
)


@pytest.fixture
def v1_node():
    return VarNode(
        raw="${v1}",
        textfsm_repr="${v1}",
        expression="word(var-v1)",
        regex=r"\S+",
    )


@pytest.fixture
def values_by_name(v1_node):
    v = ValueNode(
        name="v1",
        regex=r"\S+",
        options=None,
        infer=v1_node,
    )
    return {"v1": v}


# ------------------------------------------------------------
# Action parsing tests
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("Next", Action(line_action="Next")),
        ("Next Foo", Action(line_action="Next", state="Foo")),
        ("Continue", Action(line_action="Continue")),
        ("Continue Bar", Action(line_action="Continue", state="Bar")),
        ("Record", Action(record_action="Record")),
        ("Record Baz", Action(record_action="Record", state="Baz")),
        ("NoRecord", Action(record_action="NoRecord")),
        ("Clear", Action(record_action="Clear")),
        ("Clearall", Action(record_action="Clearall")),
        ("EOF", Action(eof_action=True)),
        ("Error ^bad$", Action(error_pattern="^bad$")),
        ("Next.Record", Action(line_action="Next", record_action="Record")),
        (
            "Next.Record Foo",
            Action(line_action="Next", record_action="Record", state="Foo"),
        ),
        ("Next.NoRecord", Action(line_action="Next", record_action="NoRecord")),
        ("Next.Clear", Action(line_action="Next", record_action="Clear")),
        ("Next.Clearall", Action(line_action="Next", record_action="Clearall")),
        ("Continue.Record", Action(line_action="Continue", record_action="Record")),
        (
            "Continue.Clearall Bar",
            Action(line_action="Continue", record_action="Clearall", state="Bar"),
        ),
    ],
)
def test_parse_action_expr(expr, expected):
    action = parse_action_expr(expr)
    assert action == expected


# ------------------------------------------------------------
# Rule parsing tests
# ------------------------------------------------------------


def test_parse_rule_line_simple():
    rule = parse_rule_line("^foo -> Next", {})
    assert isinstance(rule, RuleNode)
    assert "".join(i.raw for i in rule.pattern.items) == "^foo"
    assert rule.actions == [Action(line_action="Next")]


def test_parse_rule_line_combined(values_by_name):
    rule = parse_rule_line("^iface ${v1} -> Next.Record Table", values_by_name)
    assert "".join(i.raw for i in rule.pattern.items) == "^iface ${v1}"
    assert rule.actions == [
        Action(line_action="Next", record_action="Record", state="Table")
    ]


def test_parse_rule_line_error():
    rule = parse_rule_line("^bad -> Error ^oops$", {})
    assert rule.actions == [Action(error_pattern="^oops$")]


def test_parse_rule_line_eof():
    rule = parse_rule_line("^done -> EOF", {})
    assert rule.actions == [Action(eof_action=True)]


# ------------------------------------------------------------
# State + template parsing tests
# ------------------------------------------------------------


def test_parse_textfsm_single_state():
    text = """
Start
  ^foo -> Next
  ^bar -> Record
"""
    ast = parse_textfsm(text, [], "")

    assert isinstance(ast, TemplateAST)
    assert len(ast.states) == 1

    state = ast.states[0]
    assert state.name == "Start"
    assert len(state.rules) == 2

    assert "".join(i.raw for i in state.rules[0].pattern.items) == "^foo"
    assert state.rules[0].actions == [Action(line_action="Next")]

    assert "".join(i.raw for i in state.rules[1].pattern.items) == "^bar"
    assert state.rules[1].actions == [Action(record_action="Record")]


def test_parse_textfsm_multiple_states():
    text = """
Value v1 (\\S+)
Value Required,List v2 (\\S+)

Start
  ^foo -> Next

Table
  ^bar -> Next.Record Table
"""
    ast = parse_textfsm(text, [], "")

    assert len(ast.states) == 2

    start = ast.states[0]
    table = ast.states[1]

    assert start.name == "Start"
    assert table.name == "Table"

    assert start.rules[0].actions == [Action(line_action="Next")]
    assert table.rules[0].actions == [
        Action(line_action="Next", record_action="Record", state="Table")
    ]
