# tests/unit/generation/engine/test_one_pass.py

from unittest.mock import MagicMock, patch

import pytest

from textfsm_ai.generation.core.models import OnePassResult
from textfsm_ai.generation.engine import one_pass

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------


@pytest.fixture
def provider_instance():
    p = MagicMock()
    p.name = "MockProvider"
    return p


@pytest.fixture
def prompt_builder_instance():
    pb = MagicMock()
    pb.one_pass_prompt.return_value = "PROMPT_TEXT"
    return pb


@pytest.fixture
def llm_raw_response():
    return "RAW_LLM_RESPONSE"


@pytest.fixture
def llm_run_result():
    return MagicMock()


# ------------------------------------------------------------
# Main test
# ------------------------------------------------------------


@patch("textfsm_ai.generation.engine.one_pass.extractor.extract")
@patch("textfsm_ai.generation.engine.one_pass.llm_extractor.extract")
@patch("textfsm_ai.generation.engine.one_pass.prompt_builder.PromptBuilder")
@patch("textfsm_ai.generation.engine.one_pass.get_provider_for_model")
def test_one_pass_run(
    mock_get_provider,
    mock_prompt_builder,
    mock_llm_extract,
    mock_extractor_extract,
    provider_instance,
    prompt_builder_instance,
    llm_raw_response,
    llm_run_result,
):
    # -----------------------------
    # Arrange
    # -----------------------------
    api_key = "KEY"
    model = "MODEL"
    sample = "interface Gi0/1"

    # provider factory returns provider instance
    mock_get_provider.return_value = lambda api_key, model: provider_instance

    # PromptBuilder instance
    mock_prompt_builder.return_value = prompt_builder_instance

    # LLM extractor returns raw LLM text
    mock_llm_extract.return_value = llm_raw_response

    # extractor.extract returns old-style llm_run_result
    mock_extractor_extract.return_value = llm_run_result

    # -----------------------------
    # Act
    # -----------------------------
    result: OnePassResult = one_pass.run(api_key, model, sample)

    # -----------------------------
    # Assert
    # -----------------------------

    # Provider factory called correctly
    mock_get_provider.assert_called_once_with(model)

    # Provider instantiated with API key + model
    provider_created = mock_get_provider.return_value(api_key, model)
    assert provider_created is provider_instance

    # PromptBuilder.one_pass_prompt called correctly
    prompt_builder_instance.one_pass_prompt.assert_called_once_with(sample)

    # LLM extractor called with correct args
    mock_llm_extract.assert_called_once_with(
        provider_instance,
        model,
        "PROMPT_TEXT",
    )

    # extractor.extract called with correct args
    mock_extractor_extract.assert_called_once_with(
        provider_name=provider_instance.name,
        model=model,
        sample=sample,
        prompt="PROMPT_TEXT",
        response=llm_raw_response,
    )

    # -----------------------------
    # Validate OnePassResult fields
    # -----------------------------
    assert isinstance(result, OnePassResult)
    assert result.prompt == "PROMPT_TEXT"
    assert result.response == llm_raw_response
    assert result.model == model
    assert result.provider == provider_instance.name

    # metadata contains llm_run
    assert "llm_run" in result.metadata
    assert result.metadata["llm_run"] is llm_run_result
