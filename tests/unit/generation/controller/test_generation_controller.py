# tests/unit/generation/controller/test_generation_controller.py

from unittest.mock import Mock

from textfsm_ai.generation.controller.generation_controller import (
    GenerationController,
    is_retryable_error,
    is_unretryable_error,
)
from textfsm_ai.generation.core.models import GenerationStage


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def make_result(template, records, ready, reason=""):
    """Utility to create a GenerationResult-like object."""
    return GenerationStage(
        template=template,
        records=records,
        metadata=None,  # controller does not inspect metadata
        reason=reason,
        ready=ready,
    )


# ---------------------------------------------------------
# Test: base attempt succeeds immediately
# ---------------------------------------------------------
def test_controller_base_success(monkeypatch):
    base_result = make_result("T1", [1], ready=True)

    mock_run = Mock(return_value=base_result)
    mock_corr = Mock()

    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run",
        mock_run,
    )
    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run_correction_prompt",
        mock_corr,
    )

    controller = GenerationController(
        "Provider", api_key="KEY", model="m", max_retries=3
    )
    result = controller.run("sample")

    # Assertions
    assert result.ready is True
    assert result.last_stage.template == "T1"
    assert result.last_stage.records == [1]
    assert result.attempts == 1
    assert result.last_stage is base_result
    assert result.stages == [base_result]

    # Behavior checks
    mock_run.assert_called_once()
    mock_corr.assert_not_called()


# ---------------------------------------------------------
# Test: base fails → correction succeeds
# ---------------------------------------------------------
def test_controller_correction_success(monkeypatch):
    base_result = make_result("BAD", [], ready=False, reason="bad template")
    corrected_result = make_result("GOOD", [1], ready=True)

    mock_run = Mock(return_value=base_result)
    mock_corr = Mock(return_value=corrected_result)

    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run",
        mock_run,
    )
    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run_correction_prompt",
        mock_corr,
    )

    controller = GenerationController(
        "Provider", api_key="KEY", model="m", max_retries=3
    )
    result = controller.run("sample")
    # Assertions

    assert result.ready is True
    assert result.last_stage.template == "GOOD"
    assert result.last_stage.records == [1]
    assert result.last_stage is corrected_result
    assert result.stages[0] == base_result
    assert result.stages[-1] == corrected_result

    # Behavior checks
    assert mock_run.call_count == 3
    mock_corr.assert_called_once()


# ---------------------------------------------------------
# Test: all attempts fail → fallback result
# ---------------------------------------------------------
def test_controller_all_fail(monkeypatch):
    base_result = make_result("BAD1", [], ready=False, reason="bad1")
    correction_result = make_result("BAD2", [], ready=False, reason="bad2")

    mock_run = Mock(return_value=base_result)
    mock_corr = Mock(return_value=correction_result)

    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run",
        mock_run,
    )
    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run_correction_prompt",
        mock_corr,
    )

    controller = GenerationController(
        "Provider", api_key="KEY", model="m", max_retries=2
    )
    result = controller.run("sample")

    # Assertions
    assert result.ready is False
    assert result.last_stage.template == "BAD2"
    assert result.last_stage.records == []
    assert result.reason == "bad2"
    assert result.attempts == 2
    assert result.last_stage is correction_result
    assert result.stages[0] == base_result
    assert result.stages[-1] == correction_result

    # Behavior checks
    assert mock_run.call_count == 2
    assert mock_corr.call_count == 2


# ---------------------------------------------------------
# Test: unretryable error stops immediately, no correction attempted
# ---------------------------------------------------------
def test_controller_stops_on_unretryable_error(monkeypatch):
    base_result = make_result(
        "", [], ready=False, reason="LLM-ERROR-authentication_error-invalid key"
    )

    mock_run = Mock(return_value=base_result)
    mock_corr = Mock()

    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run",
        mock_run,
    )
    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run_correction_prompt",
        mock_corr,
    )

    controller = GenerationController(
        "Provider", api_key="KEY", model="m", max_retries=3
    )
    result = controller.run("sample")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-authentication_error-invalid key"
    assert result.attempts == 1

    mock_run.assert_called_once()
    mock_corr.assert_not_called()


# ---------------------------------------------------------
# Test: all base attempts are retryable errors -> exhausted before
# ever entering the correction-prompt phase
# ---------------------------------------------------------
def test_controller_all_base_attempts_retryable_skips_correction(monkeypatch):
    base_result = make_result(
        "", [], ready=False, reason="LLM-ERROR-rate_limit-please retry later"
    )

    mock_run = Mock(return_value=base_result)
    mock_corr = Mock()

    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run",
        mock_run,
    )
    monkeypatch.setattr(
        "textfsm_ai.generation.controller.generation_controller.engine.run_correction_prompt",
        mock_corr,
    )

    controller = GenerationController(
        "Provider", api_key="KEY", model="m", max_retries=2
    )
    result = controller.run("sample")

    assert result.ready is False
    assert result.reason == "LLM-ERROR-rate_limit-please retry later"
    assert result.attempts == 2

    assert mock_run.call_count == 2
    mock_corr.assert_not_called()


# ---------------------------------------------------------
# is_unretryable_error / is_retryable_error
# ---------------------------------------------------------
def test_is_unretryable_error_empty_or_non_llm_reason():
    assert is_unretryable_error("") is False
    assert is_unretryable_error("some other failure") is False


def test_is_unretryable_error_true_for_known_types():
    assert is_unretryable_error("LLM-ERROR-authentication_error-bad key") is True
    assert is_unretryable_error("LLM-ERROR-bad_request-malformed") is True


def test_is_unretryable_error_false_for_unknown_type():
    assert is_unretryable_error("LLM-ERROR-some_weird_error-oops") is False


def test_is_retryable_error_empty_or_non_llm_reason():
    assert is_retryable_error("") is False
    assert is_retryable_error("some other failure") is False


def test_is_retryable_error_true_for_known_types():
    assert is_retryable_error("LLM-ERROR-rate_limit-too many requests") is True
    assert is_retryable_error("LLM-ERROR-timeout-took too long") is True


def test_is_retryable_error_false_for_unknown_type():
    assert is_retryable_error("LLM-ERROR-some_weird_error-oops") is False
