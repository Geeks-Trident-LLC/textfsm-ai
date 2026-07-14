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
    # OpenRouter is a model AGGREGATOR - it re-exposes nearly every
    # other provider's catalog under "vendor/model" namespaces (e.g.
    # "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"), plus its
    # own "openrouter/auto" meta-model. Vendor slugs like "openai/",
    # "anthropic/", "google/", "deepseek/" (note: slash, not hyphen -
    # doesn't collide with the native "deepseek-" rule), "x-ai/", and
    # lowercase "qwen/" (doesn't collide with Together's capitalized
    # "Qwen/" - startswith() is case-sensitive) are all safe to claim.
    # "meta-llama/" and "mistralai/" are DELIBERATELY NOT claimed here
    # even though OpenRouter hosts models under those same slugs too -
    # Together already claims those exact prefixes, and a model string
    # like "meta-llama/Llama-3.3-70b-Instruct-Turbo" is inherently
    # ambiguous between "call via Together" and "call via OpenRouter"
    # under simple prefix matching; there is no ordering fix for a
    # true shared-prefix collision like this (unlike Cerebras' cases,
    # where a more specific sub-prefix existed). OpenRouter's curated
    # and default models are deliberately chosen to avoid this pair of
    # vendor slugs. Explicit `--provider openrouter` selection (which
    # doesn't consult this routing table) is unaffected either way.
    #
    # route() and select_provider() both return on the FIRST matching
    # rule (order matters, this is not longest-prefix-match), so a more
    # specific prefix (e.g. "deepseek-ai/") must be listed before a
    # shorter prefix it would otherwise be swallowed by (e.g.
    # "deepseek-"), since "deepseek-ai/..." legitimately starts with
    # "deepseek-" too.
    #
    # Mistral AI, unlike every other native (non-aggregator) provider
    # above, has no single shared prefix across its catalog - it spans
    # several sub-brands with genuinely different name shapes:
    # "mistral-" (large/medium/small tiers), "magistral-" (reasoning
    # line), "ministral-" (small edge models), "open-mistral-" (open-
    # weight models like Nemo), "codestral" (code-specialized, no
    # trailing hyphen since some names are exactly "codestral-latest"
    # but the family itself is just "codestral"), and "pixtral-"
    # (vision). All six prefixes are verified collision-free against
    # every rule above - most notably, "mistral-" is a different string
    # from Together's "mistralai/" (diverges at the 8th character) and
    # from Groq's "mixtral-" (unrelated string, not a Mistral product).
    #
    # Amazon Bedrock is a model AGGREGATOR like OpenRouter, but uses
    # "vendor.model-vN:M" IDs (dot after the vendor name) instead of
    # OpenRouter's "vendor/model" (slash). This means Bedrock's
    # "anthropic.", "meta.", "mistral.", "amazon.", "cohere." prefixes
    # are all textually distinct from every existing rule above, even
    # ones that look similar at a glance: OpenRouter's "anthropic/"
    # (slash) vs Bedrock's "anthropic." (dot) are different strings, and
    # native Mistral's "mistral-" (hyphen) vs Bedrock's "mistral."
    # (dot) likewise never collide - a model string can only start with
    # one of the two separator characters, never both. Cross-region
    # inference profile IDs (e.g. "us.anthropic.claude-...") are NOT
    # covered by these rules - see the matching gap noted in
    # BEDROCK_PATTERN's comment in models/patterns.py.
    #
    # Cohere, unlike Mistral, has ONE shared prefix across its whole
    # catalog - every model name starts with "command" (command-a,
    # command-r-plus, command-r, command-light) - so a single rule
    # covers it, same simplicity as xAI's single "grok-" rule. No
    # collision with Bedrock's "cohere." rule above: that's Bedrock's
    # own re-hosted namespace (dot after "cohere"), a completely
    # different string from native Cohere's bare "command..." IDs,
    # which have no "cohere" substring in them at all.
    #
    # Google Vertex AI is deliberately given NO routing rule at all -
    # unlike every other pairing above, this is a genuine, unresolvable
    # collision, not just a textually-similar-looking one. Vertex AI
    # serves the SAME Gemini model catalog under IDENTICAL model ID
    # strings as native Gemini (e.g. "gemini-2.5-pro" means the exact
    # same thing to both providers) - there is no distinguishing
    # separator character or namespace to key a rule on, unlike
    # Bedrock's "vendor." or OpenRouter's "vendor/". Adding a
    # "gemini-" -> "vertexai" rule would either never fire (native
    # Gemini's existing "gemini-" rule is checked first and always
    # wins) or silently steal every native Gemini call if reordered -
    # neither is acceptable. Vertex AI must always be selected
    # explicitly via --provider vertexai (generate_cmd.py's --provider
    # flag never consults this routing table), the same treatment
    # already given to OpenRouter's unclaimed meta-llama/ and
    # mistralai/ vendor slugs above.
    #
    # Oracle OCI is ALSO given no routing rule, for a related but
    # distinct reason: OCI's "vendor.model-name" scheme (e.g.
    # "meta.llama-3.3-70b-instruct", "xai.grok-3") uses the SAME "meta."
    # separator/vendor-prefix shape Bedrock already claims for its own
    # re-hosted Meta namespace. Unlike Vertex AI's case (identical
    # strings), OCI's actual model ID strings likely differ from
    # Bedrock's (OCI has no "-vN:M" version suffix), but the shared
    # "meta." PREFIX is still a genuine ambiguity for prefix-based
    # routing - whichever rule is listed first would silently claim
    # every "meta."-prefixed model, right or wrong, for both providers'
    # entire Meta catalogs. OCI must always be selected explicitly via
    # --provider oci.
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
            RoutingRule("openrouter/", "openrouter"),
            RoutingRule("openai/", "openrouter"),
            RoutingRule("anthropic/", "openrouter"),
            RoutingRule("google/", "openrouter"),
            RoutingRule("deepseek/", "openrouter"),
            RoutingRule("x-ai/", "openrouter"),
            RoutingRule("qwen/", "openrouter"),
            RoutingRule("moonshot-", "moonshot"),
            RoutingRule("kimi-", "moonshot"),
            RoutingRule("mistral-", "mistral"),
            RoutingRule("magistral-", "mistral"),
            RoutingRule("ministral-", "mistral"),
            RoutingRule("open-mistral-", "mistral"),
            RoutingRule("codestral", "mistral"),
            RoutingRule("pixtral-", "mistral"),
            RoutingRule("anthropic.", "bedrock"),
            RoutingRule("meta.", "bedrock"),
            RoutingRule("mistral.", "bedrock"),
            RoutingRule("amazon.", "bedrock"),
            RoutingRule("cohere.", "bedrock"),
            RoutingRule("ai21.", "bedrock"),
            RoutingRule("command", "cohere"),
        ]
    )
