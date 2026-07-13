# textfsm_ai/orchestrator/routing.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .errors import ProviderNotFoundError
from .provider import Provider
from .types import OrchestratorRequest


@dataclass
class RoutingRule:
    """
    Simple rule: model prefix -> provider name.
    """

    model_prefix: str
    provider_name: str


class RoutingTable:
    def __init__(self, rules):
        self.rules = rules

    def route(self, model: str) -> str:
        for rule in self.rules:
            if model.startswith(rule.model_prefix):
                return rule.provider_name
        raise ValueError(f"No routing rule for model: {model}")

    def select_provider(
        self,
        request: OrchestratorRequest,
        providers: Mapping[str, Provider],
    ) -> Provider:
        model = request.model

        # 1. explicit prefix rules
        for rule in self.rules:
            if model.startswith(rule.model_prefix):
                provider = providers.get(rule.provider_name)
                if provider is None:
                    raise ProviderNotFoundError(
                        f"Routing rule points to unknown provider: {rule.provider_name}"
                    )
                return provider

        # 2. fallback: ask providers if they support the model
        for provider in providers.values():
            if provider.supports(model):
                return provider

        raise ProviderNotFoundError(f"No provider found for model: {model}")


# ---------------------------------------------------------------------------
# Default routing table used by the orchestrator factory
# ---------------------------------------------------------------------------


def create_default_routing_table() -> RoutingTable:
    # Groq hosts open models (Llama, Gemma, Qwen, Mixtral) rather than a
    # single vendor-prefixed family, so it needs one rule per family it
    # serves. None of these collide with another provider's models today;
    # if a future provider hosts the same open-weight models under the
    # same names, these rules will need to be reconciled at that point.
    #
    # Together AI also hosts open models, but under "vendor/Model-Name"
    # namespaces (e.g. "meta-llama/Llama-3.3-70B-Instruct-Turbo"), so it
    # needs one rule per vendor namespace it serves. This is NOT an
    # exhaustive list of every vendor Together hosts - just the ones in
    # our curated model set; add more namespaces as needed.
    #
    # Fireworks AI also hosts open models, but under a single shared
    # "accounts/fireworks/models/" namespace for its first-party
    # catalog, so one rule covers it (unlike Together's multi-vendor
    # namespaces). Third-party/fine-tuned models under other Fireworks
    # accounts ("accounts/<other>/models/...") are not covered here.
    #
    # Cerebras also hosts bare, un-namespaced open models (like Groq),
    # and its catalog genuinely overlaps Groq's family prefixes
    # ("llama-", "qwen-") and OpenAI's "gpt-" prefix (both host the
    # open-weight "gpt-oss" models). Cerebras' specific sub-prefixes
    # ("gpt-oss-", "llama-4-", "qwen-3-") are listed BEFORE the broader
    # rules they'd otherwise be swallowed by. This does NOT resolve
    # every possible collision - e.g. Cerebras' bare "llama-3.3-70b"
    # would still match Groq's "llama-" rule first (Groq's
    # "llama-3.3-70b-versatile" is a different, longer string, but the
    # prefix-match mechanism can't tell "llama-3.3-70b" apart from a
    # prefix of it) - so that exact model name is deliberately left out
    # of Cerebras' curated/default set until routing supports more than
    # simple prefix matching.
    #
    # route() and select_provider() both return on the FIRST matching
    # rule (order matters, this is not longest-prefix-match), so a more
    # specific prefix (e.g. "deepseek-ai/") must be listed before a
    # shorter prefix it would otherwise be swallowed by (e.g.
    # "deepseek-"), since "deepseek-ai/..." legitimately starts with
    # "deepseek-" too.
    return RoutingTable(
        rules=[
            RoutingRule("gpt-oss-", "cerebras"),  # must precede "gpt-" (OpenAI)
            RoutingRule("gpt-", "openai"),
            RoutingRule("o1-", "openai"),  # Omni 1
            RoutingRule("o3-", "openai"),  # Omni 3
            RoutingRule("claude-", "anthropic"),
            RoutingRule("gemini-", "gemini"),
            RoutingRule("azure-", "azure"),
            RoutingRule("deepseek-ai/", "together"),
            RoutingRule("deepseek-", "deepseek"),
            RoutingRule("llama-4-", "cerebras"),  # must precede "llama-" (Groq)
            RoutingRule("qwen-3-", "cerebras"),  # must precede "qwen-" (Groq)
            RoutingRule("llama-", "groq"),
            RoutingRule("gemma", "groq"),
            RoutingRule("qwen-", "groq"),
            RoutingRule("mixtral-", "groq"),
            RoutingRule("grok-", "xai"),
            RoutingRule("meta-llama/", "together"),
            RoutingRule("Qwen/", "together"),
            RoutingRule("mistralai/", "together"),
            RoutingRule("accounts/fireworks/models/", "fireworks"),
            RoutingRule("llama3.", "cerebras"),  # e.g. "llama3.1-8b" (no hyphen)
            RoutingRule("sonar", "perplexity"),
        ]
    )
