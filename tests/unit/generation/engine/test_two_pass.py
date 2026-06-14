# tests/unit/generation/engine/test_two_pass.py

from unittest.mock import MagicMock, patch

from textfsm_ai.generation.core.models import TwoPassResult
from textfsm_ai.generation.engine import two_pass


@patch("textfsm_ai.generation.engine.two_pass.extractor.next_extract")
@patch("textfsm_ai.generation.engine.two_pass.extractor.extract")
@patch("textfsm_ai.generation.engine.two_pass.llm_extractor.extract")
@patch("textfsm_ai.generation.engine.two_pass.prompt_builder.PromptBuilder")
@patch("textfsm_ai.generation.engine.two_pass.get_provider_for_model")
def test_two_pass_run(
    mock_get_provider,
    mock_prompt_builder,
    mock_llm_extract,
    mock_extractor_extract,
    mock_next_extract,
):
    api_key = "dummy-key"
    model = "dummy-model"
    sample = "interface Gi0/1"

    # ------------------------------------------------------------
    # Mock provider
    # ------------------------------------------------------------
    provider_instance = MagicMock()
    provider_instance.name = "MockProvider"
    mock_get_provider.return_value = lambda api_key, model: provider_instance

    # ------------------------------------------------------------
    # Mock PromptBuilder
    # ------------------------------------------------------------
    pb_instance = MagicMock()
    pb_instance.two_pass_prompt_a.return_value = "PROMPT_A"
    pb_instance.two_pass_prompt_b.return_value = "PROMPT_B"
    mock_prompt_builder.return_value = pb_instance

    # ------------------------------------------------------------
    # Mock llm_extractor.extract
    # Pass 1 returns RESPONSE_A
    # Pass 2 returns RESPONSE_B
    # ------------------------------------------------------------
    mock_llm_extract.side_effect = ["RESPONSE_A", "RESPONSE_B"]

    # ------------------------------------------------------------
    # Mock extractor.extract (first pass)
    # ------------------------------------------------------------
    llm_run_result = MagicMock()
    mock_extractor_extract.return_value = llm_run_result

    # ------------------------------------------------------------
    # Run two_pass
    # ------------------------------------------------------------
    result: TwoPassResult = two_pass.run(api_key, model, sample)

    # ------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------

    # Provider factory called correctly
    mock_get_provider.assert_called_once_with(model)

    # Prompt A built correctly
    pb_instance.two_pass_prompt_a.assert_called_once_with(sample)

    # LLM called for pass 1
    mock_llm_extract.assert_any_call(provider_instance, model, "PROMPT_A")

    # extractor.extract called for pass 1
    mock_extractor_extract.assert_called_once_with(
        provider_name="MockProvider",
        model=model,
        sample=sample,
        prompt="PROMPT_A",
        response="RESPONSE_A",
    )

    # Prompt B built correctly using response1
    pb_instance.two_pass_prompt_b.assert_called_once_with("RESPONSE_A")

    # LLM called for pass 2
    mock_llm_extract.assert_any_call(provider_instance, model, "PROMPT_B")

    # next_extract called correctly
    mock_next_extract.assert_called_once_with(
        llm_run_result=llm_run_result,
        prompt="PROMPT_B",
        response="RESPONSE_B",
    )

    # ------------------------------------------------------------
    # Validate TwoPassResult fields
    # ------------------------------------------------------------
    assert isinstance(result, TwoPassResult)

    assert result.prompt_free == "PROMPT_A"
    assert result.response_free == "RESPONSE_A"

    assert result.prompt_structured == "PROMPT_B"
    assert result.response_structured == "RESPONSE_B"

    assert result.model == model
    assert result.provider == "MockProvider"

    # metadata contains llm_run
    assert "llm_run" in result.metadata
    assert result.metadata["llm_run"] is llm_run_result
