import json

from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.core.package import (
    Debug,
    Default,
    DeliveryOutput,
    Info,
    LLMInfo,
    LLMResponse,
    LLMStructuredResponse,
    Output,
    Quiet,
    Status,
    Usage,
    Version,
)
from textfsm_ai.dsl.core.models import DSLPipeline
from textfsm_ai.generation.core.models import GenerationPipeline

# ============================================================
# Version
# ============================================================


def test_version_to_string_includes_all_versions():
    v = Version(
        python_version="3.12.0", textfsm_version="1.1.3", textfsm_ai_version="0.4.0"
    )
    text = v.to_string()

    assert "Versions" in text
    assert "Python     : 3.12.0" in text
    assert "TextFSM    : 1.1.3" in text
    assert "TextFSM-AI : 0.4.0" in text


# ============================================================
# LLMInfo
# ============================================================


def test_llm_info_to_string_without_endpoint_shows_model():
    info = LLMInfo(
        provider_name="openai", model="gpt-4o-mini", api_key="sk-1234567890abcd"
    )
    text = info.to_string()

    assert "LLM Info" in text
    assert "Provider    : openai" in text
    assert "Model       : gpt-4o-mini" in text
    assert "Deployment" not in text
    assert "Endpoint" not in text
    # api key must be masked, never printed in full
    assert "sk-1234567890abcd" not in text


def test_llm_info_to_string_with_endpoint_shows_deployment_fields():
    info = LLMInfo(
        provider_name="azure",
        model="gpt-4o-deployment",
        api_key="sk-1234567890abcd",
        endpoint="https://example.azure.com",
        api_version="2024-02-15-preview",
    )
    text = info.to_string()

    assert "Deployment  : gpt-4o-deployment" in text
    assert "Endpoint    : https://example.azure.com" in text
    assert "API Version : 2024-02-15-preview" in text
    assert "Model       :" not in text


def test_llm_info_to_string_bedrock_shows_region_not_api_key():
    info = LLMInfo(
        provider_name="bedrock",
        model="anthropic.claude-haiku-4-5-v1:0",
        region="us-east-1",
    )
    text = info.to_string()

    assert "Provider    : bedrock" in text
    assert "Model       : anthropic.claude-haiku-4-5-v1:0" in text
    assert "Region      : us-east-1" in text
    assert "API Key     : <not used, resolved via AWS credential chain>" in text
    assert "Deployment" not in text
    assert "Endpoint" not in text


def test_llm_info_to_string_vertexai_shows_region_and_project_not_api_key():
    info = LLMInfo(
        provider_name="vertexai",
        model="gemini-2.5-flash",
        region="us-central1",
        project="my-gcp-project",
    )
    text = info.to_string()

    assert "Provider    : vertexai" in text
    assert "Model       : gemini-2.5-flash" in text
    assert "Region      : us-central1" in text
    assert "Project     : my-gcp-project" in text
    assert "API Key     : <not used, resolved via GCP ADC credential chain>" in text
    assert "Deployment" not in text
    assert "Endpoint" not in text


def test_llm_info_to_string_oci_shows_region_and_compartment_not_api_key():
    info = LLMInfo(
        provider_name="oci",
        model="meta.llama-3.3-70b-instruct",
        region="us-chicago-1",
        compartment_id="ocid1.compartment.oc1..fake",
    )
    text = info.to_string()

    assert "Provider    : oci" in text
    assert "Model       : meta.llama-3.3-70b-instruct" in text
    assert "Region      : us-chicago-1" in text
    assert "Compartment : ocid1.compartment.oc1..fake" in text
    assert (
        "API Key     : <not used, resolved via ~/.oci/config credential file>" in text
    )
    assert "Deployment" not in text
    assert "Endpoint" not in text


# ============================================================
# LLMResponse
# ============================================================


def test_llm_response_to_string_includes_duration_retries_and_raw_json():
    resp = LLMResponse(
        raw={"id": "abc123", "choices": []}, duration_ms=500, max_retries=3
    )
    text = resp.to_string()

    assert "LLM Response" in text
    assert "Duration (ms) : 500" in text
    assert "Max Retries   : 3" in text
    assert '"id": "abc123"' in text


# ============================================================
# LLMStructuredResponse
# ============================================================


def test_llm_structured_response_to_string_with_content():
    resp = LLMStructuredResponse(
        template="Value FOO (\\S+)",
        records=[{"FOO": "bar"}],
        variables={"FOO": "word"},
        handling=["identified FOO as word"],
    )
    text = resp.to_string()

    assert "LLM Structured Response" in text
    assert "Value FOO" in text
    assert '"FOO": "bar"' in text
    assert '"FOO": "word"' in text
    assert "identified FOO as word" in text


def test_llm_structured_response_to_string_empty_template_shows_placeholder():
    resp = LLMStructuredResponse()
    text = resp.to_string()

    assert "<empty>" in text


# ============================================================
# Usage
# ============================================================


def test_usage_to_string_without_warning():
    usage = Usage(
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        llm_duration_ms=250.5,
        input_per_million=1.5,
        output_per_million=3.0,
        estimated_cost=0.0001234,
    )
    text = usage.to_string()

    assert "LLM Usage" in text
    assert "Input Tokens       : 100" in text
    assert "Output Tokens      : 50" in text
    assert "Total Tokens       : 150" in text
    assert "Estimated Cost     : $0.000123" in text
    assert "Warning" not in text


def test_usage_to_string_with_warning():
    usage = Usage(warning="cost estimate unavailable for this model")
    text = usage.to_string()

    assert "Warning            : cost estimate unavailable for this model" in text


# ============================================================
# Output
# ============================================================


def test_output_to_string_without_recognizers():
    out = Output(raw_template="raw", template="final", readable_dsl="dsl text")
    text = out.to_string()

    assert "raw" in text
    assert "final" in text
    assert "dsl text" in text
    assert "<none>" in text


def test_output_to_string_with_recognizers():
    out = Output(recognizers=["^foo", "^bar"])
    text = out.to_string()

    assert '"^foo"' in text
    assert '"^bar"' in text


def test_output_to_string_empty_fields_show_placeholder():
    out = Output()
    text = out.to_string()

    assert text.count("<empty>") == 3  # raw_template, template, readable_dsl


# ============================================================
# Status
# ============================================================


def test_status_bool_reflects_passed():
    assert bool(Status(passed=True)) is True
    assert bool(Status(passed=False)) is False


def test_status_error_joins_errors():
    status = Status(errors=["first issue", "second issue"])
    assert status.error == "first issue\nsecond issue"


def test_status_exit_code():
    assert Status(passed=True).exit_code == 0
    assert Status(passed=False).exit_code == 1


def test_status_to_string_success():
    text = Status(state="generation", passed=True).to_string()
    assert text == "=== SUCCESS: generation ==="


def test_status_to_string_failure_with_errors():
    text = Status(state="generation", passed=False, errors=["boom"]).to_string()
    assert text == "=== FAIL: generation ===\nboom"


def test_status_to_string_failure_without_errors():
    text = Status(state="generation", passed=False).to_string()
    assert text == "=== FAIL: generation ===\n<none>"


def test_status_to_string_no_state_uses_placeholder():
    text = Status(passed=False).to_string()
    assert "<no-state>" in text


# ============================================================
# Quiet
# ============================================================


def test_quiet_to_string_success_returns_template():
    quiet = Quiet(template="the template", status=Status(passed=True))
    assert quiet.to_string() == "the template"


def test_quiet_to_string_success_empty_template_uses_placeholder():
    quiet = Quiet(template="", status=Status(passed=True))
    assert quiet.to_string() == "<empty-template>"


def test_quiet_to_string_failure_returns_status_string():
    quiet = Quiet(status=Status(state="parse", passed=False, errors=["bad input"]))
    assert quiet.to_string() == "=== FAIL: parse ===\nbad input"


# ============================================================
# Default
# ============================================================


def test_default_to_string_success_returns_output():
    default = Default(output=Output(template="tmpl"), status=Status(passed=True))
    text = default.to_string()
    assert "tmpl" in text


def test_default_to_string_failure_returns_status_string():
    default = Default(status=Status(state="parse", passed=False, errors=["bad input"]))
    assert default.to_string() == "=== FAIL: parse ===\nbad input"


# ============================================================
# Info
# ============================================================


def test_info_to_string_includes_all_sections():
    info = Info(
        version=Version(
            python_version="3.12.0", textfsm_version="1.1.3", textfsm_ai_version="0.4.0"
        ),
        llm_info=LLMInfo(
            provider_name="openai", model="gpt-4o-mini", api_key="sk-1234"
        ),
        usage=Usage(input_tokens=10),
        llm_structured_response=LLMStructuredResponse(template="tmpl"),
        output=Output(template="final output"),
        status=Status(passed=True),
    )
    text = info.to_string()

    assert "Status : PASS" in text
    assert "3.12.0" in text
    assert "openai" in text
    assert "Input Tokens       : 10" in text
    assert "final output" in text


def test_info_to_string_status_fail():
    info = Info(status=Status(passed=False))
    text = info.to_string()
    assert "Status : FAIL" in text


# ============================================================
# Debug
# ============================================================


def test_debug_to_string_all_fields_none():
    debug = Debug(status=Status(passed=True))
    text = debug.to_string()

    assert "Status        : PASS" in text
    assert (
        text.count("<none>") == 5
    )  # llm_info, llm_response, usage, generation_pipeline, dsl_pipeline


def test_debug_to_string_all_fields_populated():
    debug = Debug(
        llm_info=LLMInfo(
            provider_name="openai", model="gpt-4o-mini", api_key="sk-1234"
        ),
        llm_response=LLMResponse(raw={"id": "abc"}),
        usage=Usage(input_tokens=5),
        generation_pipeline=GenerationPipeline(model="gpt-4o-mini"),
        dsl_pipeline=DSLPipeline(reason="ok", ready=True),
        status=Status(passed=False),
        duration_ms=123.4,
    )
    text = debug.to_string()

    assert "Status        : FAIL" in text
    assert "Duration (ms) : 123.4" in text
    assert "openai" in text
    assert '"id": "abc"' in text
    assert "Input Tokens       : 5" in text
    assert "Generation Pipeline" in text
    assert "DSL Pipeline" in text
    # generation_pipeline/dsl_pipeline are rendered via their own to_json()
    assert json.loads(debug.generation_pipeline.to_json())["model"] == "gpt-4o-mini"


# ============================================================
# DeliveryOutput
# ============================================================


def test_delivery_output_bool_reflects_passed():
    assert bool(DeliveryOutput(mode=DeliveryMode.DEFAULT, passed=True)) is True
    assert bool(DeliveryOutput(mode=DeliveryMode.DEFAULT, passed=False)) is False


def test_delivery_output_exit_code():
    assert DeliveryOutput(mode=DeliveryMode.DEFAULT, passed=True).exit_code == 0
    assert DeliveryOutput(mode=DeliveryMode.DEFAULT, passed=False).exit_code == 1
