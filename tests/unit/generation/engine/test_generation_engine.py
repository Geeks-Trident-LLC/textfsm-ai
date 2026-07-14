# tests/unit/generation/engine/test_generation_engine.py

import pytest

from textfsm_ai.generation.core.models import (
    GenerationStage,
    LLMResponse,
    StructuredResponse,
)
from textfsm_ai.generation.engine import generation_engine


# ---------------------------------------------------------
# Mock provider + registry
# ---------------------------------------------------------
class MockProvider:
    name = "MockProvider"

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model


def mock_get_provider_by_name(model):
    return MockProvider


# ---------------------------------------------------------
# Fixtures for monkeypatching
# ---------------------------------------------------------
@pytest.fixture
def patch_provider(monkeypatch):
    monkeypatch.setattr(
        generation_engine,
        "get_provider_by_name",
        mock_get_provider_by_name,
    )


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


# ---------------------------------------------------------
# Tests for run()
# ---------------------------------------------------------
def test_run_success(patch_provider, patch_prompt_builder, monkeypatch):
    # Mock extractor.extract → returns LLMResponse
    raw_resp = LLMResponse(
        content='{"template":"T","records":[1],"variables":{},"handling":[]}',
        prompt="p",
        provider="MockProvider",
        model="m",
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.extractor,
        "extract",
        lambda provider, model, prompt: raw_resp,
    )

    # Mock structured_extractor.extract
    structured = StructuredResponse(
        template="T",
        records=[1],
        variables={},
        handling=[],
        response=raw_resp,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor,
        "extract",
        lambda resp: structured,
    )

    # Mock generator.generate
    final = GenerationStage(
        template="T",
        records=[1],
        metadata=structured,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.generator,
        "generate",
        lambda s: final,
    )

    result = generation_engine.run("Provider", "KEY", "m", "sample")

    assert isinstance(result, GenerationStage)
    assert result.ready is True
    assert result.template == "T"
    assert result.records == [1]


def test_run_bedrock_passes_region_instead_of_api_key(
    patch_prompt_builder, monkeypatch
):
    # Bedrock has no project-level api_key - the provider is constructed
    # as provider_type(region, model), not provider_type(api_key, model).
    captured = {}

    class MockBedrockProvider:
        name = "bedrock"

        def __init__(self, region, model):
            self.region = region
            self.model = model

    monkeypatch.setattr(
        generation_engine, "get_provider_by_name", lambda name: MockBedrockProvider
    )

    raw_resp = LLMResponse(
        content='{"template":"T","records":[1],"variables":{},"handling":[]}',
        prompt="p",
        provider="bedrock",
        model="m",
        ready=True,
    )

    def fake_extract(provider, model, prompt):
        captured["provider"] = provider
        return raw_resp

    monkeypatch.setattr(generation_engine.extractor, "extract", fake_extract)

    structured = StructuredResponse(
        template="T",
        records=[1],
        variables={},
        handling=[],
        response=raw_resp,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor, "extract", lambda resp: structured
    )

    final = GenerationStage(template="T", records=[1], metadata=structured, ready=True)
    monkeypatch.setattr(generation_engine.generator, "generate", lambda s: final)

    generation_engine.run(
        "bedrock", "unused-api-key", "m", "sample", region="us-east-1"
    )

    assert captured["provider"].region == "us-east-1"
    assert captured["provider"].model == "m"


def test_run_vertexai_passes_project_and_region_instead_of_api_key(
    patch_prompt_builder, monkeypatch
):
    # Vertex AI has no project-level api_key - the provider is constructed
    # as provider_type(project, region, model), not provider_type(api_key,
    # model).
    captured = {}

    class MockVertexAIProvider:
        name = "vertexai"

        def __init__(self, project, region, model):
            self.project = project
            self.region = region
            self.model = model

    monkeypatch.setattr(
        generation_engine, "get_provider_by_name", lambda name: MockVertexAIProvider
    )

    raw_resp = LLMResponse(
        content='{"template":"T","records":[1],"variables":{},"handling":[]}',
        prompt="p",
        provider="vertexai",
        model="m",
        ready=True,
    )

    def fake_extract(provider, model, prompt):
        captured["provider"] = provider
        return raw_resp

    monkeypatch.setattr(generation_engine.extractor, "extract", fake_extract)

    structured = StructuredResponse(
        template="T",
        records=[1],
        variables={},
        handling=[],
        response=raw_resp,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor, "extract", lambda resp: structured
    )

    final = GenerationStage(template="T", records=[1], metadata=structured, ready=True)
    monkeypatch.setattr(generation_engine.generator, "generate", lambda s: final)

    generation_engine.run(
        "vertexai",
        "unused-api-key",
        "m",
        "sample",
        region="us-central1",
        project="my-project",
    )

    assert captured["provider"].project == "my-project"
    assert captured["provider"].region == "us-central1"
    assert captured["provider"].model == "m"


# ---------------------------------------------------------
# Tests for run_correction_prompt()
# ---------------------------------------------------------
def test_run_correction_prompt_success(
    patch_provider, patch_prompt_builder, monkeypatch
):
    # Previous result metadata
    prev_raw = LLMResponse(
        content="PREV_JSON",
        prompt="p",
        provider="MockProvider",
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

    # Mock validator.find_template_issues
    class DummyFinding:
        findings = ["err1", "err2"]
        ready = False

    monkeypatch.setattr(
        generation_engine.validator,
        "find_template_issues",
        lambda t, r, s: DummyFinding(),
    )

    # Mock extractor.extract
    new_raw = LLMResponse(
        content='{"template":"NEW","records":[2],"variables":{},"handling":[]}',
        prompt="p",
        provider="MockProvider",
        model="m",
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.extractor,
        "extract",
        lambda provider, model, prompt: new_raw,
    )

    # Mock structured_extractor.extract
    new_structured = StructuredResponse(
        template="NEW",
        records=[2],
        variables={},
        handling=[],
        response=new_raw,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor,
        "extract",
        lambda resp: new_structured,
    )

    # Mock generator.generate
    final = GenerationStage(
        template="NEW",
        records=[2],
        metadata=new_structured,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.generator,
        "generate",
        lambda s: final,
    )

    result = generation_engine.run_correction_prompt(
        "provider", "KEY", "m", "sample", prev_result
    )

    assert isinstance(result, GenerationStage)
    assert result.ready is True
    assert result.template == "NEW"
    assert result.records == [2]


def test_run_correction_prompt_bedrock_passes_region_instead_of_api_key(
    patch_prompt_builder, monkeypatch
):
    captured = {}

    class MockBedrockProvider:
        name = "bedrock"

        def __init__(self, region, model):
            self.region = region
            self.model = model

    monkeypatch.setattr(
        generation_engine, "get_provider_by_name", lambda name: MockBedrockProvider
    )

    prev_raw = LLMResponse(
        content="PREV_JSON", prompt="p", provider="bedrock", model="m", ready=True
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

    new_raw = LLMResponse(
        content='{"template":"NEW","records":[2],"variables":{},"handling":[]}',
        prompt="p",
        provider="bedrock",
        model="m",
        ready=True,
    )

    def fake_extract(provider, model, prompt):
        captured["provider"] = provider
        return new_raw

    monkeypatch.setattr(generation_engine.extractor, "extract", fake_extract)

    new_structured = StructuredResponse(
        template="NEW",
        records=[2],
        variables={},
        handling=[],
        response=new_raw,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor, "extract", lambda resp: new_structured
    )

    final = GenerationStage(
        template="NEW", records=[2], metadata=new_structured, ready=True
    )
    monkeypatch.setattr(generation_engine.generator, "generate", lambda s: final)

    generation_engine.run_correction_prompt(
        "bedrock", "unused-api-key", "m", "sample", prev_result, region="eu-central-1"
    )

    assert captured["provider"].region == "eu-central-1"
    assert captured["provider"].model == "m"


def test_run_correction_prompt_vertexai_passes_project_and_region_instead_of_api_key(
    patch_prompt_builder, monkeypatch
):
    captured = {}

    class MockVertexAIProvider:
        name = "vertexai"

        def __init__(self, project, region, model):
            self.project = project
            self.region = region
            self.model = model

    monkeypatch.setattr(
        generation_engine, "get_provider_by_name", lambda name: MockVertexAIProvider
    )

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

    new_raw = LLMResponse(
        content='{"template":"NEW","records":[2],"variables":{},"handling":[]}',
        prompt="p",
        provider="vertexai",
        model="m",
        ready=True,
    )

    def fake_extract(provider, model, prompt):
        captured["provider"] = provider
        return new_raw

    monkeypatch.setattr(generation_engine.extractor, "extract", fake_extract)

    new_structured = StructuredResponse(
        template="NEW",
        records=[2],
        variables={},
        handling=[],
        response=new_raw,
        ready=True,
    )
    monkeypatch.setattr(
        generation_engine.structured_extractor, "extract", lambda resp: new_structured
    )

    final = GenerationStage(
        template="NEW", records=[2], metadata=new_structured, ready=True
    )
    monkeypatch.setattr(generation_engine.generator, "generate", lambda s: final)

    generation_engine.run_correction_prompt(
        "vertexai",
        "unused-api-key",
        "m",
        "sample",
        prev_result,
        region="asia-northeast1",
        project="my-project",
    )

    assert captured["provider"].project == "my-project"
    assert captured["provider"].region == "asia-northeast1"
    assert captured["provider"].model == "m"
