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
    assert table.route("meta-llama/Llama-3.3-70B-Instruct-Turbo") == "together"
    assert table.route("Qwen/Qwen2.5-32B-Instruct") == "together"
    assert table.route("mistralai/Mixtral-8x7B-Instruct-v0.1") == "together"
    assert table.route("deepseek-ai/DeepSeek-R1-Distill-Llama-70B") == "together"
    assert (
        table.route("accounts/fireworks/models/llama-v3p3-70b-instruct") == "fireworks"
    )
    assert table.route("llama-4-maverick-17b-128e-instruct") == "cerebras"
    assert table.route("qwen-3-32b") == "cerebras"
    assert table.route("llama3.1-8b") == "cerebras"
    assert table.route("gpt-oss-120b") == "cerebras"
    assert table.route("sonar") == "perplexity"
    assert table.route("sonar-pro") == "perplexity"
    assert table.route("openrouter/auto") == "openrouter"
    assert table.route("openai/gpt-4o") == "openrouter"
    assert table.route("anthropic/claude-3.5-sonnet") == "openrouter"
    assert table.route("google/gemini-2.5-flash-lite") == "openrouter"
    assert table.route("deepseek/deepseek-r1") == "openrouter"
    assert table.route("x-ai/grok-4") == "openrouter"
    assert table.route("qwen/qwen-2.5-72b-instruct") == "openrouter"
    assert table.route("moonshot-v1-8k") == "moonshot"
    assert table.route("kimi-k2-0711-preview") == "moonshot"
    assert table.route("mistral-large-latest") == "mistral"
    assert table.route("magistral-medium-latest") == "mistral"
    assert table.route("ministral-8b-latest") == "mistral"
    assert table.route("open-mistral-nemo") == "mistral"
    assert table.route("codestral-latest") == "mistral"
    assert table.route("pixtral-large-latest") == "mistral"
    assert table.route("anthropic.claude-opus-4-8-v1:0") == "bedrock"
    assert table.route("meta.llama4-maverick-v1:0") == "bedrock"
    assert table.route("mistral.mistral-large-2-v1:0") == "bedrock"
    assert table.route("amazon.titan-text-premier-v1:0") == "bedrock"
    assert table.route("cohere.command-r-plus-v1:0") == "bedrock"
    assert table.route("ai21.jamba-1-5-large-v1:0") == "bedrock"
    assert table.route("command-a") == "cohere"
    assert table.route("command-r-plus") == "cohere"
    assert table.route("command-r") == "cohere"
    assert table.route("command-light") == "cohere"


def test_deepseek_ai_prefix_does_not_collide_with_native_deepseek_rule():
    # "deepseek-ai/..." (Together) starts with "deepseek-" too, so the more
    # specific rule must be checked first or this would misroute to the
    # native DeepSeek provider.
    table = create_default_routing_table()
    assert table.route("deepseek-v4-pro") == "deepseek"
    assert table.route("deepseek-ai/DeepSeek-R1") == "together"


def test_cerebras_specific_prefixes_do_not_collide_with_broader_rules():
    # Cerebras hosts open-weight families that overlap Groq's broad
    # "llama-"/"qwen-" rules and OpenAI's "gpt-" rule (gpt-oss is an
    # open-weight model hosted by multiple providers). The Cerebras-
    # specific sub-prefixes ("llama-4-", "qwen-3-", "gpt-oss-") must be
    # checked before those broader rules, without swallowing the
    # existing Groq/OpenAI models that legitimately match them.
    table = create_default_routing_table()
    assert table.route("gpt-4o") == "openai"
    assert table.route("llama-3.3-70b-versatile") == "groq"
    assert table.route("qwen-2.5-32b") == "groq"


def test_openrouter_does_not_claim_together_vendor_slugs():
    # OpenRouter also hosts models under "meta-llama/" and "mistralai/"
    # namespaces, identical to Together's, but those prefixes are
    # deliberately NOT claimed for OpenRouter (a true shared-prefix
    # collision has no ordering fix) - Together's existing routing must
    # be unaffected.
    table = create_default_routing_table()
    assert table.route("meta-llama/Llama-3.3-70B-Instruct-Turbo") == "together"
    assert table.route("mistralai/Mixtral-8x7B-Instruct-v0.1") == "together"
    assert table.route("Qwen/Qwen2.5-32B-Instruct") == "together"


def test_mistral_prefixes_do_not_collide_with_together_or_groq():
    # Mistral's "mistral-" prefix is a different string from Together's
    # "mistralai/" (diverges at the 8th character) and from Groq's
    # "mixtral-" (an unrelated MoE model name, not a Mistral product) -
    # confirm neither existing route is disturbed.
    table = create_default_routing_table()
    assert table.route("mistralai/Mixtral-8x7B-Instruct-v0.1") == "together"
    assert table.route("mixtral-8x7b-32768") == "groq"
    assert table.route("mistral-large-latest") == "mistral"


def test_bedrock_prefixes_do_not_collide_with_openrouter_or_native_mistral():
    # Bedrock uses "vendor.model" (dot) IDs, distinct from OpenRouter's
    # "vendor/model" (slash) and native Mistral's "mistral-" (hyphen) -
    # confirm all three coexist without any route being disturbed.
    table = create_default_routing_table()
    assert table.route("anthropic/claude-3.5-sonnet") == "openrouter"
    assert table.route("anthropic.claude-opus-4-8-v1:0") == "bedrock"
    assert table.route("mistral-large-latest") == "mistral"
    assert table.route("mistral.mistral-large-2-v1:0") == "bedrock"


def test_cohere_prefix_does_not_collide_with_bedrock_cohere_namespace():
    # Native Cohere's bare "command..." IDs share no substring with
    # Bedrock's "cohere." re-hosted namespace - confirm both coexist.
    table = create_default_routing_table()
    assert table.route("command-r-plus") == "cohere"
    assert table.route("cohere.command-r-plus-v1:0") == "bedrock"


def test_vertexai_is_not_auto_routed_and_falls_to_native_gemini():
    # Vertex AI has NO routing rule at all - it serves identical model ID
    # strings to native Gemini (e.g. "gemini-2.5-pro" means the same thing
    # to both), a genuine unresolvable collision. A bare model string
    # always routes to native "gemini"; Vertex AI must be selected
    # explicitly via --provider vertexai instead.
    table = create_default_routing_table()
    assert table.route("gemini-2.5-pro") == "gemini"
    assert table.route("gemini-2.5-flash") == "gemini"
