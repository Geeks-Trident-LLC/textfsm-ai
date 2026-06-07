from textfsm_ai.generation.extractor import (
    LLMRunResult,
    extract,
    next_extract,
)

# ------------------------------------------------------------
# LLMRunResult tests
# ------------------------------------------------------------


def test_llm_run_result_initialization():
    result = LLMRunResult(
        provider="deepseek",
        model="deepseek-chat",
        sample="interface Gi0/1",
        prompt="prompt text",
        response="raw response",
    )

    assert result.provider == "deepseek"
    assert result.model == "deepseek-chat"
    assert result.sample == "interface Gi0/1"
    assert result.prompt == "prompt text"
    assert result.response == "raw response"
    assert result.next_prompt is None
    assert result.next_response is None


def test_llm_run_result_to_dict():
    result = LLMRunResult(
        provider="openai",
        model="gpt-4",
        sample="show version",
        prompt="prompt text",
        response="raw response",
        next_prompt="next prompt",
        next_response="next response",
    )

    d = result.to_dict()

    assert d["provider"] == "openai"
    assert d["model"] == "gpt-4"
    assert d["sample"] == "show version"
    assert d["prompt"] == "prompt text"
    assert d["response"] == "raw response"
    assert d["next_prompt"] == "next prompt"
    assert d["next_response"] == "next response"


# ------------------------------------------------------------
# extract() tests
# ------------------------------------------------------------


def test_extract_creates_llm_run_result():
    provider_name = "deepseek"
    model = "deepseek-chat"
    sample = "interface Gi0/1"
    prompt = "prompt text"
    response = "raw response"

    result = extract(provider_name, model, sample, prompt, response)

    assert isinstance(result, LLMRunResult)
    assert result.provider == provider_name
    assert result.model == model
    assert result.sample == sample
    assert result.prompt == prompt
    assert result.response == response
    assert result.next_prompt is None
    assert result.next_response is None


# ------------------------------------------------------------
# next_extract() tests
# ------------------------------------------------------------


def test_next_extract_updates_existing_result():
    result = LLMRunResult(
        provider="deepseek",
        model="deepseek-chat",
        sample="sample",
        prompt="first prompt",
        response="first response",
    )

    next_prompt = "second prompt"
    next_response = "second response"

    next_extract(result, next_prompt, next_response)

    assert result.next_prompt == next_prompt
    assert result.next_response == next_response
