# tests/unit/test_api.py

from __future__ import annotations

import pytest

from textfsm_ai.api import ask_ai
from textfsm_ai.orchestrator.orchestrator import OrchestratorResponse


def test_api_is_callable():
    assert callable(ask_ai)


@pytest.mark.asyncio
async def test_api_runs_with_env_config(monkeypatch):
    """
    Patch orchestrator factory + config loader so ask_ai() doesn't hit
    real env or providers.
    """

    class FakeOrchestrator:
        async def run(self, req):
            return OrchestratorResponse(
                provider="fake",
                model=req.model,
                raw={"content": "ok", "ok": True},
            )

    monkeypatch.setattr(
        "textfsm_ai.api.create_orchestrator_from_config",
        lambda cfg: FakeOrchestrator(),
    )

    monkeypatch.setattr(
        "textfsm_ai.api.load_config_from_env",
        lambda: object(),
    )

    resp = await ask_ai("hello", "fake/model")

    assert isinstance(resp, OrchestratorResponse)
    assert resp.provider == "fake"
    assert resp.content == "ok"
