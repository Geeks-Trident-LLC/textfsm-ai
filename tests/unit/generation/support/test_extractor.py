# tests/unit/generation/support/test_extractor.py

from textfsm_ai.generation.core.models import LLMRawResponse, LLMResponse
from textfsm_ai.generation.support import extractor


# ---------------------------------------------------------
# Mock provider
# ---------------------------------------------------------
class MockProvider:
    name = "MockProvider"

    def __init__(self, behavior):
        """
        behavior:
          - {"raw": LLMRawResponse(...)}
        """
        self.behavior = behavior


# ---------------------------------------------------------
# Patch llm_extractor.extract
# ---------------------------------------------------------
class DummyLLMExtractor:
    def __init__(self, raw_response):
        self.raw_response = raw_response

    def __call__(self, provider, model, prompt):
        return self.raw_response


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
def test_extract_success_with_content(monkeypatch):
    raw = LLMRawResponse(
        raw={"content": "hello", "usage": {"prompt_tokens": 5, "completion_tokens": 7}},
        ready=True,
    )

    monkeypatch.setattr(
        extractor.llm_extractor,
        "extract",
        DummyLLMExtractor(raw),
    )

    provider = MockProvider({})
    result = extractor.extract(provider, model="m", prompt="p")

    assert isinstance(result, LLMResponse)
    assert result.ready is True
    assert result.content == "hello"
    assert result.input_tokens == 5
    assert result.output_tokens == 7
    assert result.total_tokens is None
    assert result.provider == "MockProvider"
    assert result.model == "m"
    assert result.prompt == "p"
    assert result.duration_ms >= 0
    assert result.sent_at.endswith("Z")
    assert result.received_at.endswith("Z")


def test_extract_success_empty_content(monkeypatch):
    raw = LLMRawResponse(raw={"content": ""}, ready=True)

    monkeypatch.setattr(
        extractor.llm_extractor,
        "extract",
        DummyLLMExtractor(raw),
    )

    provider = MockProvider({})
    result = extractor.extract(provider, model="m", prompt="p")

    assert isinstance(result, LLMResponse)
    assert result.ready is False
    assert result.content == ""
    assert "empty" in result.reason.lower()


def test_extract_failure_raw_not_ready(monkeypatch):
    raw = LLMRawResponse(raw={}, ready=False, reason="boom")

    monkeypatch.setattr(
        extractor.llm_extractor,
        "extract",
        DummyLLMExtractor(raw),
    )

    provider = MockProvider({})
    result = extractor.extract(provider, model="m", prompt="p")

    assert isinstance(result, LLMResponse)
    assert result.ready is False
    assert result.reason == "boom"
    assert result.content == ""
    assert result.raw == raw


def test_extract_usage_variants(monkeypatch):
    raw = LLMRawResponse(
        raw={
            "content": "ok",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
            },
        },
        ready=True,
    )

    monkeypatch.setattr(
        extractor.llm_extractor,
        "extract",
        DummyLLMExtractor(raw),
    )

    provider = MockProvider({})
    result = extractor.extract(provider, model="m", prompt="p")

    assert result.input_tokens == 10
    assert result.output_tokens == 20
    assert result.total_tokens == 30


def test_extract_no_usage(monkeypatch):
    raw = LLMRawResponse(raw={"content": "ok"}, ready=True)

    monkeypatch.setattr(
        extractor.llm_extractor,
        "extract",
        DummyLLMExtractor(raw),
    )

    provider = MockProvider({})
    result = extractor.extract(provider, model="m", prompt="p")

    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.total_tokens is None
