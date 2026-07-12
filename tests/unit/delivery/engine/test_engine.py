import json

from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.engine.engine import DeliveryEngine
from textfsm_ai.dsl.core.models import DSLParseResult, DSLPipeline
from textfsm_ai.generation.core.models import (
    GenerationPipeline,
    GenerationStage,
    LLMResponse,
    StructuredResponse,
)

MODEL_INFO = {
    "provider_name": "anthropic",
    "model": "claude-sonnet-4-5",
    "api_key": "sk-test-1234",
    "endpoint": "",
    "api_version": "",
}


def _make_pipelines():
    response = LLMResponse(
        content="hello",
        prompt="sample",
        provider="anthropic",
        model="claude-sonnet-4-5",
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
        ready=True,
    )
    metadata = StructuredResponse(
        template="tmpl",
        records=[{"FOO": "bar"}],
        variables={"FOO": "word"},
        handling=["identified FOO"],
        response=response,
        ready=True,
    )
    stage = GenerationStage(
        template="tmpl", records=[{"FOO": "bar"}], metadata=metadata, ready=True
    )
    gen_pipeline = GenerationPipeline(
        model="claude-sonnet-4-5", last_stage=stage, ready=True
    )

    dsl = DSLParseResult(
        raw_template="raw tmpl",
        records=[{"FOO": "bar"}],
        canonical="Value FOO (\\S+)",
        readable="readable dsl",
        recognizers=["^foo"],
        name="dsl-parse",
        ready=True,
    )
    dsl_pipeline = DSLPipeline(dsl=dsl, ready=True)

    return gen_pipeline, dsl_pipeline


def test_assemble_quiet_mode_string():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.QUIET,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert result.mode is DeliveryMode.QUIET
    assert result.output == "Value FOO (\\S+)"
    assert result.passed is True
    assert result.error == ""


def test_assemble_quiet_mode_json():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.QUIET,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        as_json=True,
    )

    parsed = json.loads(result.output)
    assert parsed["template"] == "Value FOO (\\S+)"


def test_assemble_default_mode_string():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.DEFAULT,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert result.mode is DeliveryMode.DEFAULT
    assert "Value FOO" in result.output
    assert result.passed is True


def test_assemble_default_mode_json():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.DEFAULT,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        as_json=True,
    )

    parsed = json.loads(result.output)
    assert parsed["output"]["template"] == "Value FOO (\\S+)"


def test_assemble_info_mode_string():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.INFO,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert result.mode is DeliveryMode.INFO
    assert "Status : PASS" in result.output
    assert result.passed is True


def test_assemble_info_mode_json():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.INFO,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        as_json=True,
    )

    parsed = json.loads(result.output)
    assert parsed["llm_info"]["provider_name"] == "anthropic"


def test_assemble_debug_mode_string():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.DEBUG,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        duration_ms=999,
    )

    assert result.mode is DeliveryMode.DEBUG
    assert "Duration (ms) : 999" in result.output
    assert result.passed is True


def test_assemble_debug_mode_json():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.DEBUG,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        as_json=True,
    )

    parsed = json.loads(result.output)
    assert parsed["duration_ms"] == 0


def test_assemble_unknown_mode_falls_back_to_default():
    gen_pipeline, dsl_pipeline = _make_pipelines()
    engine = DeliveryEngine()

    # Not a real DeliveryMode value; nothing prevents a caller from
    # bypassing the enum, so the trailing fallback branch is reachable.
    result = engine.assemble(
        mode=99,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert result.mode == 99
    assert "Value FOO" in result.output
    assert result.passed is True


def test_assemble_failure_propagates_error_and_passed_false():
    gen_pipeline = GenerationPipeline(model="x", last_stage=None, ready=False)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)
    engine = DeliveryEngine()

    result = engine.assemble(
        mode=DeliveryMode.DEFAULT,
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert result.passed is False
