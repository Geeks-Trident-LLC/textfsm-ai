# tests/unit/dsl/engine/test_dsl_engine.py

from unittest.mock import MagicMock, patch

from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)
from textfsm_ai.dsl.engine.dsl_engine import (
    build_machine_dsl,
    canonicalize_template,
    recognize_patterns,
    render_human_dsl,
)

# ------------------------------------------------------------
# canonicalize_template
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine.canonicalize")
def test_canonicalize_template_success(mock_canon):
    mock_canon.return_value = MagicMock(
        return_text="CANONICAL",
        reason="",
        ready=True,
    )

    result = canonicalize_template("RAW", records=[{"x": 1}])

    assert isinstance(result, CanonicalTemplate)
    assert result.template == "CANONICAL"
    assert result.llm_template == "RAW"
    assert result.records == [{"x": 1}]
    assert result.ready is True


@patch("textfsm_ai.dsl.engine.dsl_engine.canonicalize")
def test_canonicalize_template_failure(mock_canon):
    mock_canon.return_value = MagicMock(
        return_text="BAD",
        reason="canon-fail",
        ready=False,
    )

    result = canonicalize_template("RAW", records=[])

    assert result.template == "BAD"
    assert result.ready is False
    assert result.reason == "canon-fail"


# ------------------------------------------------------------
# build_machine_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._extract_machine_dsl")
def test_build_machine_dsl_success(mock_extract):
    mock_extract.return_value = MagicMock(
        reason="",
        ready=True,
    )

    canonical = CanonicalTemplate(
        llm_template="RAW",
        records=[],
        template="CANON",
        reason="",
        ready=True,
    )

    result = build_machine_dsl(canonical)

    assert isinstance(result, MachineDSL)
    assert result.canonical is canonical
    assert result.ready is True
    assert result.reason == ""


@patch("textfsm_ai.dsl.engine.dsl_engine._extract_machine_dsl")
def test_build_machine_dsl_failure(mock_extract):
    mock_extract.return_value = MagicMock(
        reason="extract-fail",
        ready=False,
    )

    canonical = CanonicalTemplate(
        llm_template="RAW",
        records=[],
        template="CANON",
        reason="",
        ready=True,
    )

    result = build_machine_dsl(canonical)

    assert result.ready is False
    assert result.reason == "extract-fail"


# ------------------------------------------------------------
# render_human_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._render_dsl")
def test_render_human_dsl_success(mock_render):
    mock_render.return_value = MagicMock(
        return_text="HUMAN",
        reason="",
        ready=True,
    )

    machine = MachineDSL(
        canonical=CanonicalTemplate(
            llm_template="RAW",
            records=[],
            template="CANON",
            reason="",
            ready=True,
        ),
        dsl=MagicMock(),
        reason="",
        ready=True,
    )

    result = render_human_dsl(machine, sample="SAMPLE")

    assert isinstance(result, HumanDSL)
    assert result.human_dsl == "HUMAN"
    assert result.template == "CANON"
    assert result.sample == "SAMPLE"
    assert result.ready is True


@patch("textfsm_ai.dsl.engine.dsl_engine.build_machine_dsl")
@patch("textfsm_ai.dsl.engine.dsl_engine._render_dsl")
def test_render_human_dsl_builds_machine_if_missing(mock_render, mock_build):
    mock_render.return_value = MagicMock(
        return_text="HUMAN",
        reason="",
        ready=True,
    )
    mock_build.return_value = MagicMock(dsl="BUILT")

    machine = MachineDSL(
        canonical=CanonicalTemplate(
            llm_template="RAW",
            records=[],
            template="CANON",
            reason="",
            ready=True,
        ),
        dsl=None,
        reason="",
        ready=True,
    )

    result = render_human_dsl(machine)

    mock_build.assert_called_once()
    assert result.human_dsl == "HUMAN"


# ------------------------------------------------------------
# recognize_patterns
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._recognize_dsl_patterns")
def test_recognize_patterns_success(mock_rec):
    mock_rec.return_value = ("PATTERNS", "DEBUG")

    machine = MachineDSL(
        canonical=CanonicalTemplate(
            llm_template="RAW",
            records=[],
            template="CANON",
            reason="",
            ready=True,
        ),
        dsl=MagicMock(),
        reason="",
        ready=True,
    )

    result = recognize_patterns(machine, sample="SAMPLE", debug=True)

    assert isinstance(result, RecognizerPatterns)
    assert result.patterns == "PATTERNS"
    assert result.debug_info == "DEBUG"
    assert result.ready is True


@patch("textfsm_ai.dsl.engine.dsl_engine._recognize_dsl_patterns")
def test_recognize_patterns_failure(mock_rec):
    mock_rec.side_effect = RuntimeError("boom")

    machine = MachineDSL(
        canonical=CanonicalTemplate(
            llm_template="RAW",
            records=[],
            template="CANON",
            reason="",
            ready=True,
        ),
        dsl=MagicMock(),
        reason="",
        ready=True,
    )

    result = recognize_patterns(machine, sample="SAMPLE")

    assert result.ready is False
    assert "RuntimeError" in result.reason
    assert result.patterns == ""
    assert list(result.debug_info.values()) == ["RuntimeError: boom"]


@patch("textfsm_ai.dsl.engine.dsl_engine.build_machine_dsl")
@patch("textfsm_ai.dsl.engine.dsl_engine._recognize_dsl_patterns")
def test_recognize_patterns_builds_machine_if_missing(mock_rec, mock_build):
    mock_rec.return_value = ("PATTERNS", "")
    mock_build.return_value = MagicMock(dsl="BUILT")

    machine = MachineDSL(
        canonical=CanonicalTemplate(
            llm_template="RAW",
            records=[],
            template="CANON",
            reason="",
            ready=True,
        ),
        dsl=None,
        reason="",
        ready=True,
    )

    result = recognize_patterns(machine)

    mock_build.assert_called_once()
    assert result.patterns == "PATTERNS"
