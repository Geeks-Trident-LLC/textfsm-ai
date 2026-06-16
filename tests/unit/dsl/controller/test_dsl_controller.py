from unittest.mock import patch

import pytest

from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.dsl.core.models import (
    CanonicalTemplate,
    HumanDSL,
    MachineDSL,
    RecognizerPatterns,
)

# ------------------------------------------------------------
# canonicalize
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.canonicalize_template")
def test_canonicalize(mock_canon):
    mock_canon.return_value = CanonicalTemplate(
        raw_template="RAW",
        template="CANON",
        records=["REC"],
    )

    controller = DSLController()
    result = controller.canonicalize("RAW", ["REC"])

    mock_canon.assert_called_once_with("RAW", ["REC"])
    assert isinstance(result, CanonicalTemplate)


def test_canonicalize_empty_template():
    controller = DSLController()
    with pytest.raises(ValueError):
        controller.canonicalize("", [])


# ------------------------------------------------------------
# to_machine_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.build_machine_dsl")
def test_to_machine_dsl(mock_build):
    canon = CanonicalTemplate("RAW", "CANON", [])
    mock_build.return_value = MachineDSL(canonical=canon, ast={"x": 1})

    controller = DSLController()
    result = controller.to_machine_dsl(canon)

    mock_build.assert_called_once_with(canon)
    assert isinstance(result, MachineDSL)


def test_to_machine_dsl_invalid_type():
    controller = DSLController()
    with pytest.raises(TypeError):
        controller.to_machine_dsl("not a canonical template")


# ------------------------------------------------------------
# to_human_dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.render_human_dsl")
def test_to_human_dsl_with_dsl(mock_render):
    canon = CanonicalTemplate("RAW", "CANON", [])
    dsl = MachineDSL(canonical=canon, ast={"x": 1})

    mock_render.return_value = HumanDSL("DSL", "CANON", "SAMP")

    controller = DSLController()
    result = controller.to_human_dsl(dsl=dsl, canonical=canon, sample="SAMP")

    mock_render.assert_called_once_with(
        dsl=dsl,
        template=canon,
        sample="SAMP",
    )
    assert isinstance(result, HumanDSL)


@patch("textfsm_ai.dsl.controller.dsl_controller.render_human_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.build_machine_dsl")
def test_to_human_dsl_auto_build_machine(mock_build, mock_render):
    canon = CanonicalTemplate("RAW", "CANON", [])
    mock_build.return_value = MachineDSL(canonical=canon, ast={"x": 1})
    mock_render.return_value = HumanDSL("DSL", "CANON", "SAMP")

    controller = DSLController()
    result = controller.to_human_dsl(dsl=None, canonical=canon, sample="SAMP")

    mock_build.assert_called_once_with(canon)
    mock_render.assert_called_once()
    assert isinstance(result, HumanDSL)


def test_to_human_dsl_missing_inputs():
    controller = DSLController()
    with pytest.raises(ValueError):
        controller.to_human_dsl(dsl=None, canonical=None)


# ------------------------------------------------------------
# recognize
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.recognize_patterns")
def test_recognize_with_dsl(mock_rec):
    canon = CanonicalTemplate("RAW", "CANON", [])
    dsl = MachineDSL(canonical=canon, ast={"x": 1})

    mock_rec.return_value = RecognizerPatterns(
        dsl=dsl,
        template=canon,
        sample="SAMP",
        patterns=["P1"],
        debug_info=None,
    )

    controller = DSLController()
    result = controller.recognize(dsl=dsl, canonical=canon, sample="SAMP")

    mock_rec.assert_called_once_with(
        dsl=dsl,
        template=canon,
        sample="SAMP",
        debug=False,
    )
    assert isinstance(result, RecognizerPatterns)


@patch("textfsm_ai.dsl.controller.dsl_controller.recognize_patterns")
@patch("textfsm_ai.dsl.controller.dsl_controller.build_machine_dsl")
def test_recognize_auto_build_machine(mock_build, mock_rec):
    canon = CanonicalTemplate("RAW", "CANON", [])
    mock_build.return_value = MachineDSL(canonical=canon, ast={"x": 1})
    mock_rec.return_value = RecognizerPatterns(
        dsl=mock_build.return_value,
        template=canon,
        sample="SAMP",
        patterns=["P1"],
        debug_info=None,
    )

    controller = DSLController()
    result = controller.recognize(dsl=None, canonical=canon, sample="SAMP")

    mock_build.assert_called_once_with(canon)
    mock_rec.assert_called_once()
    assert isinstance(result, RecognizerPatterns)


def test_recognize_missing_inputs():
    controller = DSLController()
    with pytest.raises(ValueError):
        controller.recognize(dsl=None, canonical=None)
