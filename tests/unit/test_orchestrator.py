# tests/unit/test_orchestrator.py

from __future__ import annotations

import pytest

from textfsm_ai.orchestrator.errors import ProviderRateLimitError
from textfsm_ai.orchestrator.factory import create_orchestrator
from textfsm_ai.orchestrator.orchestrator import OrchestratorRequest
from textfsm_ai.orchestrator.routing import RoutingRule, RoutingTable

from .helpers import MockProvider


@pytest.mark.asyncio
async def test_routing_selects_correct_provider():
    p1 = MockProvider("openai")
    p2 = MockProvider("azure_openai")

    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="gpt-", provider_name="openai")]
    )

    orch = create_orchestrator([p1, p2])
    orch._routing_table = routing  # inject for test

    req = OrchestratorRequest(model="gpt-4o", prompt="hi")
    resp = await orch.run(req)

    assert resp.provider == "openai"
    assert resp.content == "openai:hi"


@pytest.mark.asyncio
async def test_retry_on_rate_limit(monkeypatch):
    p = MockProvider("openai", behavior="rate_limit")

    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="gpt-", provider_name="openai")]
    )

    orch = create_orchestrator([p])
    orch._routing_table = routing
    orch._max_retries = 1

    calls = []

    async def generate_side_effect(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise ProviderRateLimitError("rate limited")
        return {"content": "ok"}

    p.generate = generate_side_effect  # type: ignore[assignment]

    req = OrchestratorRequest(model="gpt-4o", prompt="hi")
    resp = await orch.run(req)

    assert resp.content == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_reraises_last_exception_after_all_retries_exhausted():
    # Unlike test_retry_on_rate_limit (fails once, then succeeds), this
    # provider ALWAYS rate-limits - retries must exhaust across every
    # candidate provider and the orchestrator must re-raise the last
    # exception it saw, rather than swallowing it or hanging.
    p = MockProvider("openai", behavior="rate_limit")

    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="gpt-", provider_name="openai")]
    )

    orch = create_orchestrator([p])
    orch._routing_table = routing
    orch._max_retries = 1

    req = OrchestratorRequest(model="gpt-4o", prompt="hi")

    with pytest.raises(ProviderRateLimitError, match="rate limited"):
        await orch.run(req)

    assert p.calls == 2  # initial attempt + 1 retry, both exhausted


@pytest.mark.asyncio
async def test_async_orchestrator_basic():
    p = MockProvider("openai")
    orch = create_orchestrator([p])

    req = OrchestratorRequest(model="gpt-4o", prompt="hi")
    resp = await orch.run(req)

    assert resp.content == "openai:hi"
    assert resp.provider == "openai"


@pytest.mark.asyncio
async def test_fallback_on_provider_error():
    primary = MockProvider("primary", behavior="error")
    fallback = MockProvider("fallback", behavior="ok")

    routing = RoutingTable(
        rules=[RoutingRule(model_prefix="model/", provider_name="primary")]
    )

    orch = create_orchestrator([primary, fallback])
    orch._routing_table = routing

    req = OrchestratorRequest(model="model/x", prompt="hi")
    resp = await orch.run(req)

    assert resp.provider == "fallback"
    assert resp.content == "fallback:hi"
