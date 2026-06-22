from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.dsl.engine.recognizer.dsl_recognizer import (
    _build_literal_regex,
    _build_variable_map,
    _build_variable_pattern,
    recognize_dsl_patterns,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_dsl(vars=None, states=None):
    return MagicMock(
        variables=vars or [],
        states=states or [],
    )


PUNCTS_GROUP = r"[!-/:-@\[-`{-~]+"

# ------------------------------------------------------------
# _build_literal_regex
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.PUNCTS_GROUP", PUNCTS_GROUP)
@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.DIGITS", r"\d+")
@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.NUMBER", r"\d+")
@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.infer_base_keyword")
def test_literal_regex_basic(mock_infer):
    mock_infer.return_value = "word"

    assert _build_literal_regex("abc") == "abc"
    assert _build_literal_regex("abc def") == r"abc\s+def"


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.PUNCTS_GROUP", PUNCTS_GROUP)
@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.infer_base_keyword")
def test_literal_regex_puncts_group(mock_infer):
    mock_infer.return_value = "puncts"

    txt = ". . . . ."
    out = _build_literal_regex(txt)
    assert r"[!-/:-@\[-`{-~]+" in out


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.infer_base_keyword")
def test_literal_regex_number(mock_infer):
    mock_infer.return_value = "number"
    assert _build_literal_regex("123") == r"\S+" or r"\d+"


# ------------------------------------------------------------
# _build_variable_pattern
# ------------------------------------------------------------


def test_variable_pattern_basic():
    var_map = {
        "iface": r"\S+",
        "mtu": r"\d+",
    }

    pattern = "^interface ${iface} ${mtu}$"
    out = _build_variable_pattern(pattern, var_map)

    assert out == "^interface\\s+\\S+\\s+\\d+$"


def test_variable_pattern_suffix_dollars():
    var_map = {"iface": r"\S+"}
    pattern = "^abc ${iface}$$"
    out = _build_variable_pattern(pattern, var_map)
    assert out.endswith("$")  # $$ → $


def test_variable_pattern_missing_var():
    var_map = {}
    with pytest.raises(KeyError):
        _build_variable_pattern("^abc ${iface}$", var_map)


def test_variable_pattern_invalid_format():
    var_map = {"dummy": ".*"}
    with pytest.raises(KeyError):
        _build_variable_pattern("abc ${user}", var_map)


# ------------------------------------------------------------
# _build_variable_map
# ------------------------------------------------------------


def test_build_variable_map():
    dsl = make_dsl(
        vars=[
            {"name": "iface", "expression_regex": r"\S+"},
            {"name": "mtu", "expression_regex": r"\d+"},
        ]
    )

    out = _build_variable_map(dsl)
    assert out == {"iface": r"\S+", "mtu": r"\d+"}


# ------------------------------------------------------------
# recognize_dsl_patterns — variable case
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer._build_variable_pattern")
def test_recognize_variable_patterns(mock_build):
    mock_build.return_value = r"^iface \S+$"

    dsl = make_dsl(
        vars=[{"name": "iface", "expression_regex": r"\S+"}],
        states=[
            {
                "name": "Start",
                "transitions": [{"pattern": "^iface ${iface}$"}],
            }
        ],
    )

    out, debug = recognize_dsl_patterns(dsl, template=None, sample="iface eth0")
    assert "^iface \\S+$" in out
    mock_build.assert_called_once()


# ------------------------------------------------------------
# recognize_dsl_patterns — literal case
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer._build_literal_regex")
def test_recognize_literal_patterns(mock_lit):
    mock_lit.return_value = r"abc\s+123"

    dsl = make_dsl(
        states=[
            {
                "name": "Start",
                "transitions": [{"pattern": "^abc 123$"}],
            }
        ]
    )

    out, debug = recognize_dsl_patterns(dsl, template=None, sample="abc 123")
    assert "^abc\\s+123$" in out


# ------------------------------------------------------------
# recognize_dsl_patterns — invalid literal regex
# ------------------------------------------------------------


def test_recognize_invalid_literal_pattern():
    dsl = make_dsl(
        states=[
            {
                "name": "Start",
                "transitions": [{"pattern": "[invalid"}],  # bad regex
            }
        ]
    )

    out, debug = recognize_dsl_patterns(dsl, template=None, sample="abc")
    assert out.strip() == ""  # no valid patterns


# ------------------------------------------------------------
# recognize_dsl_patterns — template fallback
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.recognizer.dsl_recognizer.extract_machine_dsl")
def test_recognize_template_fallback(mock_extract):
    mock_extract.return_value = make_dsl(states=[])

    out, debug = recognize_dsl_patterns(
        dsl=None,
        template="Value iface (\\S+)",
        sample="abc",
    )

    mock_extract.assert_called_once()
