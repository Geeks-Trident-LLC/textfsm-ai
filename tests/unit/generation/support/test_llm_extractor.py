# tests/unit/generation/support/test_llm_extractor.py

from textfsm_ai.generation.support import llm_extractor


class DummyProvider:
    def __init__(self, response_dict):
        self.response_dict = response_dict
        self.called_with = None

    def generate_sync(self, prompt, model):
        # record call for assertion
        self.called_with = (prompt, model)
        return self.response_dict


def test_llm_extractor_returns_content():
    provider = DummyProvider({"content": "hello world"})
    model = "dummy-model"
    prompt = "test prompt"

    result = llm_extractor.extract(provider, model, prompt)

    assert result == "hello world"
    assert provider.called_with == (prompt, model)


def test_llm_extractor_missing_content_returns_empty_string():
    provider = DummyProvider({"other_key": "ignored"})
    model = "dummy-model"
    prompt = "test prompt"

    result = llm_extractor.extract(provider, model, prompt)

    assert result == ""


def test_llm_extractor_content_none_returns_empty_string():
    provider = DummyProvider({"content": None})
    model = "dummy-model"
    prompt = "test prompt"

    result = llm_extractor.extract(provider, model, prompt)

    assert result == ""
