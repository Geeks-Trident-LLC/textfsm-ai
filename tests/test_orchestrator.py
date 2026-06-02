# tests/test_orchestrator.py
import pytest

from textfsm_ai.orchestrator.errors import ProviderRateLimitError
from textfsm_ai.orchestrator.factory import create_orchestrator
from textfsm_ai.orchestrator.routing import RoutingRule, RoutingTable
from textfsm_ai.orchestrator.types import OrchestratorRequest

from .helpers import MockProvider  # or wherever you put it


def test_routing_selects_correct_provider():
    p1 = MockProvider("openai")
    p2 = MockProvider("azure_openai")
    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="openai/", provider_name="openai")]
    )
    orch = create_orchestrator([p1, p2])
    orch._routing_table = routing  # inject for test

    req = OrchestratorRequest(model="openai/gpt-4o", prompt="hi")
    resp = orch.run(req)

    assert resp.provider == "openai"
    assert resp.content == "openai:hi"


def test_retry_on_rate_limit(monkeypatch):
    p = MockProvider("openai", behavior="rate_limit")
    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="openai/", provider_name="openai")]
    )
    orch = create_orchestrator([p])
    orch._routing_table = routing
    orch._max_retries = 1

    # first call rate_limit, second ok
    calls = []

    def generate_side_effect(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise ProviderRateLimitError("rate limited")
        return {"content": "ok"}

    p.generate = generate_side_effect  # type: ignore[assignment]

    req = OrchestratorRequest(model="openai/gpt-4o", prompt="hi")
    resp = orch.run(req)

    assert resp.content == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_async_orchestrator_basic():
    p = MockProvider("openai")
    orch = create_orchestrator([p])
    req = OrchestratorRequest(model="openai/gpt-4o", prompt="hi")
    resp = await orch.run_async(req)
    assert resp.content == "openai:hi"


def test_fallback_on_provider_error():
    primary = MockProvider("primary", behavior="error")
    fallback = MockProvider("fallback", behavior="ok")

    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="model/", provider_name="primary")]
    )

    orch = create_orchestrator([primary, fallback])
    orch._routing_table = routing

    req = OrchestratorRequest(model="model/x", prompt="hi")
    resp = orch.run(req)

    assert resp.provider == "fallback"
    assert resp.content == "fallback:hi"
