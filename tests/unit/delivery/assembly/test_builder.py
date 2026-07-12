from types import SimpleNamespace

from textfsm_ai.delivery.assembly.builder import build_delivery_package
from textfsm_ai.dsl.core.models import DSLParseResult, DSLPipeline
from textfsm_ai.generation.core.models import (
    GenerationPipeline,
    GenerationStage,
    LLMRawResponse,
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


def _make_generation_pipeline(*, last_stage=None, max_retries=1):
    return GenerationPipeline(
        model="claude-sonnet-4-5",
        last_stage=last_stage,
        max_retries=max_retries,
        ready=True,
    )


def _make_stage(*, metadata=None, name="generate", reason=""):
    return GenerationStage(
        template="",
        records=[],
        metadata=metadata,
        name=name,
        reason=reason,
        ready=True,
    )


def _make_metadata(
    *, response=None, template="", records=None, variables=None, handling=None
):
    return StructuredResponse(
        template=template,
        records=records or [],
        variables=variables or {},
        handling=handling or [],
        response=response,
        ready=True,
    )


def _make_response(
    *, raw=None, input_tokens=10, output_tokens=20, total_tokens=30, duration_ms=500
):
    return LLMResponse(
        content="hello",
        prompt="sample",
        provider="anthropic",
        model="claude-sonnet-4-5",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        duration_ms=duration_ms,
        raw=raw,
        ready=True,
    )


def _make_dsl(
    *, canonical="Value FOO (\\S+)", raw_template="raw tmpl", reason="", ready=True
):
    return DSLParseResult(
        raw_template=raw_template,
        records=[{"FOO": "bar"}],
        canonical=canonical,
        readable="readable dsl",
        recognizers=["^foo"],
        name="dsl-parse",
        ready=ready,
        reason=reason,
    )


def test_full_happy_path():
    response = _make_response(raw=LLMRawResponse(raw={"id": "abc"}))
    metadata = _make_metadata(
        response=response, template="tmpl", variables={"FOO": "word"}
    )
    stage = _make_stage(metadata=metadata)
    gen_pipeline = _make_generation_pipeline(last_stage=stage)

    dsl = _make_dsl()
    dsl_pipeline = DSLPipeline(dsl=dsl, ready=True)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
        duration_ms=1234,
    )

    assert pkg.quiet.template == "Value FOO (\\S+)"
    assert pkg.quiet.status.passed is True
    assert pkg.default.output.template == "Value FOO (\\S+)"
    assert pkg.default.status.passed is True
    assert pkg.info.llm_info.provider_name == "anthropic"
    assert pkg.info.usage.input_tokens == 10
    assert pkg.info.usage.output_tokens == 20
    assert pkg.info.usage.total_tokens == 30
    assert pkg.info.usage.estimated_cost > 0
    assert pkg.info.usage.warning == ""
    assert pkg.info.llm_structured_response.variables == {"FOO": "word"}
    assert pkg.debug.duration_ms == 1234
    assert pkg.debug.generation_pipeline is gen_pipeline
    assert pkg.debug.dsl_pipeline is dsl_pipeline


def test_minimal_empty_path_no_stage_no_dsl():
    gen_pipeline = _make_generation_pipeline(last_stage=None)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.quiet.template == ""
    assert pkg.quiet.status.passed is False
    assert pkg.default.output.raw_template == ""
    assert pkg.default.output.template == ""
    assert pkg.default.output.recognizers == []
    assert pkg.info.usage.input_tokens == 0
    assert pkg.info.status.state == ""


def test_stage_present_but_metadata_none():
    stage = _make_stage(metadata=None)
    gen_pipeline = _make_generation_pipeline(last_stage=stage)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.info.usage.input_tokens == 0
    assert pkg.info.llm_structured_response.template == ""
    # quiet falls back to metadata.template, but metadata is None -> ""
    assert pkg.quiet.template == ""


def test_errors_collects_dsl_reason():
    dsl = _make_dsl(reason="dsl validation failed", ready=False)
    dsl_pipeline = DSLPipeline(dsl=dsl, ready=False)
    gen_pipeline = _make_generation_pipeline(last_stage=None)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert "dsl validation failed" in pkg.default.status.errors
    assert pkg.default.status.passed is False


def test_errors_collects_generation_stage_reason_when_dsl_missing():
    stage = _make_stage(metadata=None, reason="generation failed")
    gen_pipeline = _make_generation_pipeline(last_stage=stage)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert "generation failed" in pkg.default.status.errors
    assert pkg.default.status.state == "generate"


def test_status_passed_reflects_dsl_ready_false():
    dsl = _make_dsl(ready=False)
    dsl_pipeline = DSLPipeline(dsl=dsl, ready=False)
    gen_pipeline = _make_generation_pipeline(last_stage=None)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.default.status.passed is False


def test_quiet_template_falls_back_to_raw_template_when_canonical_empty():
    dsl = _make_dsl(canonical="", raw_template="raw only")
    dsl_pipeline = DSLPipeline(dsl=dsl, ready=True)
    gen_pipeline = _make_generation_pipeline(last_stage=None)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.quiet.template == "raw only"


def test_quiet_template_uses_metadata_template_when_dsl_missing():
    metadata = _make_metadata(template="metadata template text")
    stage = _make_stage(metadata=metadata)
    gen_pipeline = _make_generation_pipeline(last_stage=stage)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=MODEL_INFO,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.quiet.template == "metadata template text"


def test_model_auto_inferred_from_raw_payload_when_missing():
    model_info = {**MODEL_INFO, "model": ""}
    raw_obj = SimpleNamespace(model="inferred-model-xyz")
    response = _make_response(raw=LLMRawResponse(raw={"raw": raw_obj}))
    metadata = _make_metadata(response=response)
    stage = _make_stage(metadata=metadata)
    gen_pipeline = _make_generation_pipeline(last_stage=stage)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=model_info,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.info.llm_info.model == "inferred-model-xyz"


def test_unknown_pricing_model_produces_warning():
    model_info = {
        **MODEL_INFO,
        "provider_name": "anthropic",
        "model": "totally-unknown-model",
    }
    response = _make_response()
    metadata = _make_metadata(response=response)
    stage = _make_stage(metadata=metadata)
    gen_pipeline = _make_generation_pipeline(last_stage=stage)
    dsl_pipeline = DSLPipeline(dsl=None, ready=False)

    pkg = build_delivery_package(
        model_info=model_info,
        generation_pipeline=gen_pipeline,
        dsl_pipeline=dsl_pipeline,
    )

    assert pkg.info.usage.warning != ""
    assert pkg.info.usage.estimated_cost == 0.0
