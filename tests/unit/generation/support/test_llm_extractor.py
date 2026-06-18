# tests/unit/generation/support/test_llm_extractor.py


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
