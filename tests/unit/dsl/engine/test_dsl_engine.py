# tests/unit/dsl/engine/test_dsl_engine.py

from unittest.mock import MagicMock, patch

import textfsm_ai.dsl.engine.dsl_engine as dsl_engine
from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)

# ------------------------------------------------------------
# canonicalize_template
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine.TemplateCanonicalizer")
def test_canonicalize_template(mock_canon_cls):
    mock_instance = MagicMock()
    mock_instance.canonicalize.return_value = "CANONICAL"
    mock_canon_cls.return_value = mock_instance

    result = dsl_engine.canonicalize_template("RAW", ["REC"])

    mock_instance.canonicalize.assert_called_once_with("RAW", ["REC"])

    assert isinstance(result, CanonicalTemplate)
    assert result.raw_template == "RAW"
    assert result.canonical_template == "CANONICAL"
    assert result.records_sample == ["REC"]


# ------------------------------------------------------------
# build_machine_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._extract_machine_dsl")
def test_build_machine_dsl(mock_extract):
    mock_extract.return_value = {"ast": "X"}

    canon = CanonicalTemplate(
        raw_template="RAW",
        canonical_template="CANON",
        records_sample=[],
    )

    result = dsl_engine.build_machine_dsl(canon)

    mock_extract.assert_called_once_with("CANON")

    assert isinstance(result, MachineDSL)
    assert result.canonical_template is canon
    assert result.ast == {"ast": "X"}


# ------------------------------------------------------------
# render_human_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._render_dsl")
def test_render_human_dsl(mock_render):
    mock_render.return_value = "HUMAN_DSL"

    canon = CanonicalTemplate(
        raw_template="RAW",
        canonical_template="CANON",
        records_sample=[],
    )
    dsl = MachineDSL(canonical_template=canon, ast={"ast": "X"})

    result = dsl_engine.render_human_dsl(dsl=dsl, template=canon, sample="SAMP")

    mock_render.assert_called_once_with(
        dsl={"ast": "X"},
        template="CANON",
        sample="SAMP",
    )

    assert isinstance(result, HumanDSL)
    assert result.dsl_text == "HUMAN_DSL"
    assert result.template_preview == "CANON"
    assert result.sample == "SAMP"


# ------------------------------------------------------------
# recognize_patterns
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._recognize_dsl_patterns")
def test_recognize_patterns(mock_recognize):
    mock_recognize.return_value = (["P1", "P2"], {"debug": True})

    canon = CanonicalTemplate(
        raw_template="RAW",
        canonical_template="CANON",
        records_sample=[],
    )
    dsl = MachineDSL(canonical_template=canon, ast={"ast": "X"})

    result = dsl_engine.recognize_patterns(
        dsl=dsl,
        template=canon,
        sample="SAMP",
        debug=True,
    )

    mock_recognize.assert_called_once_with(
        dsl={"ast": "X"},
        template="CANON",
        sample="SAMP",
        debug=True,
    )

    assert isinstance(result, RecognizerPatterns)
    assert result.patterns == ["P1", "P2"]
    assert result.debug_info == {"debug": True}
    assert result.sample == "SAMP"
    assert result.dsl is dsl
    assert result.template is canon


# ------------------------------------------------------------
# recognize_patterns (debug=False)
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.engine.dsl_engine._recognize_dsl_patterns")
def test_recognize_patterns_no_debug(mock_recognize):
    mock_recognize.return_value = (["P"], {"debug": True})

    canon = CanonicalTemplate(
        raw_template="RAW",
        canonical_template="CANON",
        records_sample=[],
    )
    dsl = MachineDSL(canonical_template=canon, ast={"ast": "X"})

    result = dsl_engine.recognize_patterns(
        dsl=dsl,
        template=canon,
        sample="SAMP",
        debug=False,
    )

    # debug_info must be stripped
    assert result.debug_info is None
    assert result.patterns == ["P"]
