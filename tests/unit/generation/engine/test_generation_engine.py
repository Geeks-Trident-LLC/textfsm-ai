# tests/unit/generation/engine/test_generation_engine.py

import pytest

from textfsm_ai.generation.core.models import (
    GenerationStage,
    LLMResponse,
    StructuredResponse,
)
from textfsm_ai.generation.engine import generation_engine


# ---------------------------------------------------------
# Fixtures for monkeypatching
# ---------------------------------------------------------
@pytest.fixture
def patch_prompt_builder(monkeypatch):
    class DummyPB:
        def base_prompt(self, sample):
            return f"BASE:{sample}"

        def correction_prompt(self, sample, prev, findings):
            return f"CORR:{sample}:{prev}:{findings}"

    monkeypatch.setattr(
        generation_engine.prompt_builder,
        "PromptBuilder",
        lambda: DummyPB(),
    )


def _install_extractor_capture(monkeypatch, captured, raw_resp):
    def fake_extract(provider_name, model, prompt, **kwargs):
        captured["provider_name"] = provider_name
        captured["model"] = model
        captured["prompt"] = prompt
        captured["kwargs"] = kwargs
        return raw_resp

    monkeypatch.setattr(generation_engine.extractor, "extract", fake_extract)


def _install_pipeline_passthrough(monkeypatch, template, records):
    structured = StructuredResponse(
        template=template,
        records=records,
        variables={},
        handling=[],
        response=None,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor, "extract", lambda resp: structured
    )

    final = GenerationStage(
        template=template, records=records, metadata=structured, ready=True
    )
    monkeypatch.setattr(generation_engine.generator, "generate", lambda s: final)
    return final


# ---------------------------------------------------------
# Tests for run()
# ---------------------------------------------------------
def test_run_success(patch_prompt_builder, monkeypatch):
    captured = {}
    raw_resp = LLMResponse(
        content='{"template":"T","records":[1],"variables":{},"handling":[]}',
        prompt="p",
        provider="anthropic",
        model="m",
        ready=True,
    )
    _install_extractor_capture(monkeypatch, captured, raw_resp)
    _install_pipeline_passthrough(monkeypatch, "T", [1])

    result = generation_engine.run("anthropic", "KEY", "m", "sample")

    assert isinstance(result, GenerationStage)
    assert result.ready is True
    assert result.template == "T"
    assert result.records == [1]

    assert captured["provider_name"] == "anthropic"
    assert captured["model"] == "m"
    assert captured["prompt"] == "BASE:sample"
    assert captured["kwargs"]["api_key"] == "KEY"
    assert captured["kwargs"]["deployment"] == "m"


def test_run_passes_all_construction_fields_unconditionally(
    patch_prompt_builder, monkeypatch
):
    # No more provider-specific branching: every resolved field is
    # forwarded regardless of provider name, and anyask.ask() ignores
    # whatever a given provider doesn't need.
    captured = {}
    raw_resp = LLMResponse(
        content='{"template":"T","records":[1],"variables":{},"handling":[]}',
        prompt="p",
        provider="bedrock",
        model="m",
        ready=True,
    )
    _install_extractor_capture(monkeypatch, captured, raw_resp)
    _install_pipeline_passthrough(monkeypatch, "T", [1])

    generation_engine.run(
        "bedrock",
        "unused-api-key",
        "m",
        "sample",
        region="us-east-1",
        project="my-project",
        compartment_id="ocid1.compartment.oc1..fake",
    )

    kwargs = captured["kwargs"]
    assert kwargs["region"] == "us-east-1"
    assert kwargs["project"] == "my-project"
    assert kwargs["compartment_id"] == "ocid1.compartment.oc1..fake"
    assert kwargs["api_key"] == "unused-api-key"


# ---------------------------------------------------------
# Tests for run_correction_prompt()
# ---------------------------------------------------------
def test_run_correction_prompt_success(patch_prompt_builder, monkeypatch):
    prev_raw = LLMResponse(
        content="PREV_JSON",
        prompt="p",
        provider="anthropic",
        model="m",
        ready=True,
    )
    prev_structured = StructuredResponse(
        template="OLD_TEMPLATE",
        records=[1],
        variables={},
        handling=[],
        response=prev_raw,
        ready=True,
    )
    prev_result = GenerationStage(
        template="OLD_TEMPLATE",
        records=[1],
        metadata=prev_structured,
        ready=False,
    )

    class DummyFinding:
        findings = ["err1", "err2"]
        ready = False

    monkeypatch.setattr(
        generation_engine.validator,
        "find_template_issues",
        lambda t, r, s: DummyFinding(),
    )

    captured = {}
    new_raw = LLMResponse(
        content='{"template":"NEW","records":[2],"variables":{},"handling":[]}',
        prompt="p",
        provider="anthropic",
        model="m",
        ready=True,
    )
    _install_extractor_capture(monkeypatch, captured, new_raw)
    _install_pipeline_passthrough(monkeypatch, "NEW", [2])

    result = generation_engine.run_correction_prompt(
        "anthropic", "KEY", "m", "sample", prev_result
    )

    assert isinstance(result, GenerationStage)
    assert result.ready is True
    assert result.template == "NEW"
    assert result.records == [2]

    assert captured["provider_name"] == "anthropic"
    assert captured["prompt"] == "CORR:sample:PREV_JSON:['err1', 'err2']"


def test_run_correction_prompt_passes_all_construction_fields_unconditionally(
    patch_prompt_builder, monkeypatch
):
    prev_raw = LLMResponse(
        content="PREV_JSON", prompt="p", provider="vertexai", model="m", ready=True
    )
    prev_structured = StructuredResponse(
        template="OLD",
        records=[1],
        variables={},
        handling=[],
        response=prev_raw,
        ready=True,
    )
    prev_result = GenerationStage(
        template="OLD", records=[1], metadata=prev_structured, ready=False
    )

    class DummyFinding:
        findings = ["err1"]
        ready = False

    monkeypatch.setattr(
        generation_engine.validator,
        "find_template_issues",
        lambda t, r, s: DummyFinding(),
    )

    captured = {}
    new_raw = LLMResponse(
        content='{"template":"NEW","records":[2],"variables":{},"handling":[]}',
        prompt="p",
        provider="vertexai",
        model="m",
        ready=True,
    )
    _install_extractor_capture(monkeypatch, captured, new_raw)
    _install_pipeline_passthrough(monkeypatch, "NEW", [2])

    generation_engine.run_correction_prompt(
        "vertexai",
        "unused-api-key",
        "m",
        "sample",
        prev_result,
        region="asia-northeast1",
        project="my-project",
    )

    kwargs = captured["kwargs"]
    assert kwargs["region"] == "asia-northeast1"
    assert kwargs["project"] == "my-project"
