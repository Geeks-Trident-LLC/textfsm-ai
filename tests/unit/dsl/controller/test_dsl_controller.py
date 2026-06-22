from unittest.mock import MagicMock, patch

from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.core.models import GenerationPipeline, GenerationStage

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_gen_pipeline(ready=True, reason="", template="T", records=None, sample="S"):
    """Create a minimal GenerationPipeline with a last_stage."""
    last_stage = GenerationStage(
        name="generation-final",
        template=template,
        records=records or [],
        reason=reason,
        ready=ready,
    )

    return GenerationPipeline(
        stages=[last_stage],
        last_stage=last_stage,
        reason=reason,
        ready=ready,
        sample=sample,
    )


# ------------------------------------------------------------
# Stage 0: validate-generation
# ------------------------------------------------------------


def test_dsl_controller_invalid_generation():
    controller = DSLController()
    gen = make_gen_pipeline(ready=False, reason="bad generation")

    pipeline = controller.run(gen)
    assert not pipeline.ready
    assert pipeline.reason == "bad generation"
    assert len(pipeline.stages) == 1
    assert pipeline.stages[0].name == "validate-generation"


# ------------------------------------------------------------
# Stage 1: canonicalize-template
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_canonicalize_failure(mock_canon):
    mock_canon.return_value = MagicMock(ready=False, reason="canon-fail")

    controller = DSLController()
    gen = make_gen_pipeline()

    pipeline = controller.run(gen)

    mock_canon.assert_called_once_with("T", [])
    assert not pipeline.ready
    assert pipeline.reason == "canon-fail"
    assert pipeline.stages[-1].name == "canonicalize-template"


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_canonicalize_success(mock_canon):
    mock_canon.return_value = MagicMock(ready=True, reason="", template="C")

    controller = DSLController()
    gen = make_gen_pipeline()

    func_name = "textfsm_ai.dsl.controller.dsl_controller.engine.build_machine_dsl"
    with patch(func_name) as mock_machine:
        mock_machine.return_value = MagicMock(ready=False, reason="stop")
        pipeline = controller.run(gen)

    assert pipeline.stages[0].name == "canonicalize-template"
    assert mock_canon.called


# ------------------------------------------------------------
# Stage 2: extract-machine-dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.build_machine_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_machine_dsl_failure(mock_canon, mock_machine):
    mock_canon.return_value = MagicMock(ready=True)
    mock_machine.return_value = MagicMock(ready=False, reason="machine-fail")

    controller = DSLController()
    gen = make_gen_pipeline()

    pipeline = controller.run(gen)

    assert not pipeline.ready
    assert pipeline.reason == "machine-fail"
    assert pipeline.stages[-1].name == "extract-machine-dsl"


# ------------------------------------------------------------
# Stage 3: render-human-dsl
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.render_human_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.build_machine_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_human_dsl_failure(mock_canon, mock_machine, mock_human):
    mock_canon.return_value = MagicMock(ready=True)
    mock_machine.return_value = MagicMock(ready=True)
    mock_human.return_value = MagicMock(ready=False, reason="human-fail")

    controller = DSLController()
    gen = make_gen_pipeline()

    pipeline = controller.run(gen)

    assert not pipeline.ready
    assert pipeline.reason == "human-fail"
    assert pipeline.stages[-1].name == "render-human-dsl"


# ------------------------------------------------------------
# Stage 4: recognize-patterns
# ------------------------------------------------------------


@patch("textfsm_ai.dsl.controller.dsl_controller.engine.recognize_patterns")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.render_human_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.build_machine_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_full_success(mock_canon, mock_machine, mock_human, mock_rec):
    mock_canon.return_value = MagicMock(ready=True)
    mock_machine.return_value = MagicMock(ready=True)
    mock_human.return_value = MagicMock(ready=True)
    mock_rec.return_value = MagicMock(ready=True, reason="")

    controller = DSLController()
    gen = make_gen_pipeline()

    pipeline = controller.run(gen)

    assert pipeline.ready
    assert pipeline.last_stage.name == "recognize-patterns"
    assert len(pipeline.stages) == 4  # canonical → machine → human → recognizer

    mock_rec.assert_called_once()


# ------------------------------------------------------------
# Argument passing
# ------------------------------------------------------------
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.recognize_patterns")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.render_human_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.build_machine_dsl")
@patch("textfsm_ai.dsl.controller.dsl_controller.engine.canonicalize_template")
def test_dsl_controller_argument_passing(
    mock_canon, mock_machine, mock_human, mock_rec
):
    mock_canon.return_value = MagicMock(ready=True, template="C")
    mock_machine.return_value = MagicMock(ready=True, machine="M")
    mock_human.return_value = MagicMock(ready=True, human="H")
    mock_rec.return_value = MagicMock(ready=True)

    controller = DSLController()
    gen = make_gen_pipeline(template="T", records=[{"x": 1}], sample="S")

    controller.run(gen, debug=True)

    mock_canon.assert_called_once_with("T", [{"x": 1}])
    mock_machine.assert_called_once_with(mock_canon.return_value)

    # FIXED: render_human_dsl only receives (machine_dsl, sample)
    mock_human.assert_called_once_with(mock_machine.return_value, "S")

    # recognizer receives (canonical, sample, debug)
    mock_rec.assert_called_once_with(mock_machine.return_value, "S", debug=True)
