# tests/unit/orchestrator/test_routing.py

from __future__ import annotations

import pytest

from textfsm_ai.orchestrator.errors import ProviderNotFoundError
from textfsm_ai.orchestrator.routing import (
    RoutingRule,
    RoutingTable,
    create_default_routing_table,
)
from textfsm_ai.orchestrator.types import OrchestratorRequest


class _FakeProvider:
    def __init__(self, name: str, supports_any: bool = False):
        self.name = name
        self._supports_any = supports_any

    def supports(self, model: str) -> bool:
        return self._supports_any


# ---------------------------------------------------------
# route()
# ---------------------------------------------------------
def test_route_returns_matching_provider_name():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])
    assert table.route("gpt-4o") == "openai"


def test_route_raises_when_no_rule_matches():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])
    with pytest.raises(ValueError, match="No routing rule for model"):
        table.route("claude-opus-4-8")


# ---------------------------------------------------------
# select_provider()
# ---------------------------------------------------------
def test_select_provider_uses_matching_rule():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])
    provider = _FakeProvider("openai")

    result = table.select_provider(
        OrchestratorRequest(model="gpt-4o", prompt=""), {"openai": provider}
    )

    assert result is provider


def test_select_provider_raises_when_rule_points_to_unregistered_provider():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])

    with pytest.raises(ProviderNotFoundError, match="unknown provider: openai"):
        table.select_provider(OrchestratorRequest(model="gpt-4o", prompt=""), {})


def test_select_provider_falls_back_to_supports_check():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])
    fallback = _FakeProvider("catch-all", supports_any=True)

    result = table.select_provider(
        OrchestratorRequest(model="claude-opus-4-8", prompt=""),
        {"catch-all": fallback},
    )

    assert result is fallback


def test_select_provider_raises_when_nothing_matches():
    table = RoutingTable(rules=[RoutingRule("gpt-", "openai")])
    unhelpful = _FakeProvider("unhelpful", supports_any=False)

    with pytest.raises(ProviderNotFoundError, match="No provider found for model"):
        table.select_provider(
            OrchestratorRequest(model="claude-opus-4-8", prompt=""),
            {"unhelpful": unhelpful},
        )


# ---------------------------------------------------------
# create_default_routing_table()
# ---------------------------------------------------------
def test_create_default_routing_table_routes_known_prefixes():
    table = create_default_routing_table()

    assert table.route("gpt-4o") == "openai"
    assert table.route("o1-mini") == "openai"
    assert table.route("o3-mini") == "openai"
    assert table.route("claude-opus-4-8") == "anthropic"
    assert table.route("gemini-2.5-flash") == "gemini"
    assert table.route("azure-gpt-4o") == "azure"
    assert table.route("deepseek-v4-pro") == "deepseek"
    assert table.route("llama-3.3-70b-versatile") == "groq"
    assert table.route("gemma2-9b-it") == "groq"
    assert table.route("qwen-2.5-32b") == "groq"
    assert table.route("mixtral-8x7b-32768") == "groq"
    assert table.route("grok-4") == "xai"
