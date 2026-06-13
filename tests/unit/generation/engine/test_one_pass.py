# tests/unit/generation/engine/test_one_pass.py

from unittest.mock import MagicMock, patch

import pytest

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
def llm_result():
    r = MagicMock()
    r.response = "RAW_LLM"
    r.next_response = None
    return r


@pytest.fixture
def final_result():
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
    llm_result,
    final_result,
):
    # -----------------------------
    # Arrange
    # -----------------------------
    api_key = "KEY"
    model = "MODEL"
    sample = "interface Gi0/1"

    # provider factory returns a provider instance
    mock_get_provider.return_value = lambda api_key, model: provider_instance

    # PromptBuilder instance
    mock_prompt_builder.return_value = prompt_builder_instance

    # LLM extractor returns raw LLM output
    mock_llm_extract.return_value = llm_result

    # extractor.extract returns final structured result
    mock_extractor_extract.return_value = final_result

    # -----------------------------
    # Act
    # -----------------------------
    result = one_pass.run(api_key, model, sample)

    # -----------------------------
    # Assert
    # -----------------------------

    # Provider factory called correctly
    mock_get_provider.assert_called_once_with(model)

    # Provider instantiated with API key
    provider_instance_created = mock_get_provider.return_value(api_key, model)
    assert provider_instance_created is provider_instance

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
        provider_instance.name,
        model,
        sample,
        "PROMPT_TEXT",
        llm_result,
    )

    # Final result is returned
    assert result is final_result
