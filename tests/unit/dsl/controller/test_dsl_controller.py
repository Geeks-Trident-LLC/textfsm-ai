# tests/unit/dsl/controller/test_dsl_controller.py

from unittest.mock import Mock, patch

from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.dsl.core.models import DSLParseResult, DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline, GenerationStage

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_gen(ready=True, reason="", template="T", records=None):
    """Create a fake GenerationPipeline with minimal structure."""
    if records is None:
        records = [{"v1": "abc"}]

    last_stage = GenerationStage(
        template=template, records=records, reason=reason, ready=ready
    )

    gen = Mock(spec=GenerationPipeline)
    gen.ready = ready
    gen.reason = reason
    gen.last_stage = last_stage
    return gen


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------


def test_dsl_controller_generation_not_ready():
    """If generation failed, DSLController must return a failed DSLPipeline."""
    gen = make_gen(ready=False, reason="GEN-FAIL")

    controller = DSLController()
    out = controller.run(gen)

    assert isinstance(out, DSLPipeline)
    assert out.dsl is None
    assert out.ready is False
    assert "GENERATION-ERROR: GEN-FAIL" in out.reason


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.run")
def test_dsl_controller_engine_failure(mock_engine_run):
    """If engine.run fails, DSLController must return a failed DSLPipeline."""
    gen = make_gen(ready=True)

    mock_engine_run.return_value = DSLParseResult(
        raw_template="T", records=[{"v1": "abc"}], ready=False, reason="ENGINE-FAIL"
    )

    controller = DSLController()
    out = controller.run(gen)

    assert isinstance(out, DSLPipeline)
    assert out.dsl.ready is False
    assert out.ready is False
    assert out.reason == "ENGINE-FAIL"


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.run")
def test_dsl_controller_success(mock_engine_run):
    """If everything succeeds, DSLController must return a ready DSLPipeline."""
    gen = make_gen(ready=True)

    mock_engine_run.return_value = DSLParseResult(
        raw_template="T",
        records=[{"v1": "abc"}],
        ast="AST",
        canonical="CANONICAL",
        readable="READABLE",
        recognizers=["^foo$"],
        ready=True,
        reason="",
    )

    controller = DSLController()
    out = controller.run(gen)

    assert isinstance(out, DSLPipeline)
    assert out.dsl is mock_engine_run.return_value
    assert out.ready is True
    assert out.reason == ""
    assert out.dsl.canonical == "CANONICAL"
    assert out.dsl.readable == "READABLE"
    assert out.dsl.recognizers == ["^foo$"]
