# tests/unit/generation/controller/test_generation_controller.py

from unittest.mock import Mock

from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.generation.core.models import GenerationResult


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def make_result(template, records, ready, reason=""):
    """Utility to create a GenerationResult-like object."""
    return GenerationResult(
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

    controller = GenerationController(api_key="KEY", model="m", max_retries=3)
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

    controller = GenerationController(api_key="KEY", model="m", max_retries=3)
    result = controller.run("sample")

    # Assertions
    assert result.ready is True
    assert result.last_stage.template == "GOOD"
    assert result.last_stage.records == [1]
    assert result.attempts == 2
    assert result.last_stage is corrected_result
    assert result.stages == [base_result, corrected_result]

    # Behavior checks
    assert mock_run.call_count == 1
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

    controller = GenerationController(api_key="KEY", model="m", max_retries=2)
    result = controller.run("sample")

    # Assertions
    assert result.ready is False
    assert result.last_stage.template == "BAD2"
    assert result.last_stage.records == []
    assert result.reason == "bad2"
    assert result.attempts == 2
    assert result.last_stage is correction_result
    assert result.stages == [base_result, correction_result]

    # Behavior checks
    assert mock_run.call_count == 1
    assert mock_corr.call_count == 1
