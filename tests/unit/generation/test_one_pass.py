from unittest.mock import MagicMock, patch

from textfsm_ai.generation import one_pass


@patch("textfsm_ai.generation.one_pass.extractor.extract")
@patch("textfsm_ai.generation.one_pass.llm_extractor.extract")
@patch("textfsm_ai.generation.one_pass.prompt_builder.PromptBuilder")
@patch("textfsm_ai.generation.one_pass.get_provider_for_model")
def test_one_pass_run(
    mock_get_provider,
    mock_prompt_builder,
    mock_llm_extract,
    mock_extractor_extract,
):
    api_key = "dummy-key"
    model = "dummy-model"
    sample = "interface Gi0/1"

    # -----------------------------
    # Mock provider
    # -----------------------------
    provider_instance = MagicMock()
    provider_instance.name = "MockProvider"
    mock_get_provider.return_value = lambda api_key, model: provider_instance

    # -----------------------------
    # Mock prompt builder
    # -----------------------------
    pb_instance = MagicMock()
    pb_instance.one_pass_prompt.return_value = "PROMPT_TEXT"
    mock_prompt_builder.return_value = pb_instance

    # -----------------------------
    # Mock llm_extractor.extract
    # -----------------------------
    mock_llm_extract.return_value = "RAW_LLM_RESPONSE"

    # -----------------------------
    # Mock extractor.extract
    # -----------------------------
    mock_result = MagicMock()
    mock_extractor_extract.return_value = mock_result

    # -----------------------------
    # Run one_pass
    # -----------------------------
    result = one_pass.run(api_key, model, sample)

    # -----------------------------
    # Assertions
    # -----------------------------

    # Provider factory called correctly
    mock_get_provider.assert_called_once_with(model)

    # Provider instantiated with API key
    provider_instance = mock_get_provider.return_value(api_key, model)
    assert provider_instance is not None

    # PromptBuilder.one_pass_prompt called correctly
    pb_instance.one_pass_prompt.assert_called_once_with(sample)

    # llm_extractor.extract called with correct args
    mock_llm_extract.assert_called_once_with(provider_instance, model, "PROMPT_TEXT")

    # extractor.extract called with correct args
    mock_extractor_extract.assert_called_once_with(
        provider_instance.name,
        model,
        sample,
        "PROMPT_TEXT",
        "RAW_LLM_RESPONSE",
    )

    # Final result is whatever extractor.extract returned
    assert result is mock_result
