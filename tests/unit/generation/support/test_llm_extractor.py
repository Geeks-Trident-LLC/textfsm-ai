# tests/unit/generation/support/test_llm_extractor.py

from types import SimpleNamespace

from textfsm_ai.generation.core.models import LLMRawResponse
from textfsm_ai.generation.support.llm_extractor import extract


# ---------------------------------------------------------
# Mock Provider
# ---------------------------------------------------------
class MockProvider:
    def __init__(self, behavior):
        """
        behavior: dict controlling provider behavior
          - {"return": {...}} → return this dict
          - {"return": None} → return None
          - {"raise": Exception("msg")} → raise exception
        """
        self.behavior = behavior

    def generate_sync(self, prompt, model):
        if "raise" in self.behavior:
            raise self.behavior["raise"]
        return self.behavior.get("return")


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
def test_extract_success_nonempty():
    provider = MockProvider({"return": {"content": "hello"}})

    result = extract(provider, model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is True
    assert result.raw == {"content": "hello"}
    assert result.reason == ""


def test_extract_success_empty_dict():
    provider = MockProvider({"return": {}})

    result = extract(provider, model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.raw == {}
    assert "empty" in result.reason.lower()


def test_extract_success_none():
    provider = MockProvider({"return": None})

    result = extract(provider, model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.raw == {}
    assert "empty" in result.reason.lower()


def test_extract_exception():
    provider = MockProvider({"raise": RuntimeError("boom")})

    result = extract(provider, model="x", prompt="test")

    assert isinstance(result, LLMRawResponse)
    assert result.ready is False
    assert result.raw == {}
    assert "RuntimeError" in result.reason
    assert "boom" in result.reason


def test_extract_non_dict_response():
    provider = MockProvider({"return": "unexpected string response"})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.raw == {"raw": "unexpected string response"}
    assert "non-dict response: str" in result.reason


def test_extract_explicit_error_payload():
    provider = MockProvider(
        {"return": {"error": {"type": "rate_limit", "message": "too many requests"}}}
    )

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-rate_limit-too many requests"


def test_extract_explicit_error_payload_missing_type_and_message():
    provider = MockProvider({"return": {"error": {}}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-unknown-no-message"


def test_extract_nested_raw_object_with_error_attribute():
    raw_obj = SimpleNamespace(
        error=SimpleNamespace(type="server_error", message="internal failure")
    )
    provider = MockProvider({"return": {"raw": raw_obj}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-server_error-internal failure"


def test_extract_nested_raw_object_error_missing_attrs_uses_defaults():
    raw_obj = SimpleNamespace(error=SimpleNamespace())
    provider = MockProvider({"return": {"raw": raw_obj}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-unknown-no-message"


def test_extract_raw_object_without_error_attribute_proceeds_normally():
    raw_obj = SimpleNamespace(some_field="value")
    provider = MockProvider({"return": {"raw": raw_obj, "content": "hello"}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is True


def test_extract_missing_content_key():
    provider = MockProvider({"return": {"some_other_key": "value"}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "provider returned response without content"


def test_extract_empty_string_content():
    provider = MockProvider({"return": {"content": ""}})

    result = extract(provider, model="x", prompt="test")

    assert result.ready is False
    assert result.reason == "provider returned response without content"
