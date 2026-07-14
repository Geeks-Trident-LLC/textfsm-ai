# Providers

textfsm-ai integrates 18 LLM providers behind one interface (`generate()`,
`run_pipeline()`, and the `textfsm-ai generate` CLI command all take the
same `provider="..."` value). Most providers just need an API key; a few
cloud-gateway providers (Bedrock, Vertex AI, OCI) use their own ambient
credential chains instead and take extra parameters in place of `api_key`.

Run `textfsm-ai providers list` at any time for the live, code-derived
version of this table.

## All providers

| Provider | `provider` value | Credential | Extra params | Example model |
|---|---|---|---|---|
| OpenAI | `"openai"` | `OPENAI_API_KEY` | — | `gpt-4o-mini` |
| Anthropic | `"anthropic"` | `ANTHROPIC_API_KEY` | — | `claude-haiku-4-5-20251001` |
| Google Gemini | `"gemini"` | `GEMINI_API_KEY` | — | `gemini-2.5-flash` |
| DeepSeek | `"deepseek"` | `DEEPSEEK_API_KEY` | — | `deepseek-v4-flash` |
| Azure OpenAI | `"azure"` | `AZURE_API_KEY` | `endpoint` (`AZURE_ENDPOINT`), `api_version` (`AZURE_API_VERSION`), `model` is a deployment name (`AZURE_DEPLOYMENT`) | *(your deployment name)* |
| Groq | `"groq"` | `GROQ_API_KEY` | — | `llama-3.1-8b-instant` |
| xAI (Grok) | `"xai"` | `XAI_API_KEY` | — | `grok-3-mini` |
| Together AI | `"together"` | `TOGETHER_API_KEY` | — | `meta-llama/Llama-3.1-8B-Instruct-Turbo` |
| Fireworks AI | `"fireworks"` | `FIREWORKS_API_KEY` | — | `accounts/fireworks/models/llama-v3p1-8b-instruct` |
| Cerebras | `"cerebras"` | `CEREBRAS_API_KEY` | — | `llama3.1-8b` |
| Perplexity | `"perplexity"` | `PERPLEXITY_API_KEY` | — | `sonar` |
| OpenRouter | `"openrouter"` | `OPENROUTER_API_KEY` | — | `google/gemini-2.5-flash-lite` |
| Moonshot AI (Kimi) | `"moonshot"` | `MOONSHOT_API_KEY` | — | `moonshot-v1-8k` |
| Mistral AI | `"mistral"` | `MISTRAL_API_KEY` | — | `mistral-small-latest` |
| Amazon Bedrock | `"bedrock"` | *(none — AWS credential chain)* | `region` (`BEDROCK_REGION`/`BEDROCK_DEFAULT_REGION`, required) | `anthropic.claude-haiku-4-5-v1:0` |
| Cohere | `"cohere"` | `COHERE_API_KEY` | — | `command-light` |
| Google Vertex AI | `"vertexai"` | *(none — GCP ADC credential chain)* | `project` (`VERTEXAI_PROJECT`, required), `region` (`VERTEXAI_REGION`, required) | `gemini-2.5-flash` |
| Oracle OCI | `"oci"` | *(none — `~/.oci/config` credential file)* | `compartment_id` (`OCI_COMPARTMENT_ID`, required), `region` (`OCI_REGION`, optional — falls back to the config file) | `meta.llama-3.3-70b-instruct` |

Credentials resolve in this order everywhere: CLI flag / explicit function
argument > provider-specific environment variable > `providers.yaml`. See
the [CLI Guide](../cli/index.md) for the full flag reference and the
[Quickstart](../getting-started/quickstart.md) for Python API usage
examples, including the three cloud-gateway providers above.

## Two implementation shapes

Internally, providers fall into two groups — this only matters if you're
extending textfsm-ai itself, not for calling it:

- **Shape A** — OpenAI-compatible chat-completions API (DeepSeek, Groq,
  xAI, Together AI, Fireworks AI, Cerebras, Perplexity, OpenRouter,
  Moonshot). These share one HTTP client implementation and differ only in
  base URL, env var, and default model.
- **Shape B** — a native SDK with its own request/response shape (OpenAI,
  Anthropic, Gemini, Azure, Mistral, Bedrock, Cohere, Vertex AI, OCI).
  Bedrock, Vertex AI, and OCI additionally take extra constructor
  parameters (`region`/`project`/`compartment_id`) instead of `api_key`,
  since they authenticate via their cloud platform's own credential chain
  rather than a project-level API key.

## Routing collisions

A few providers are intentionally **not** included in the orchestrator's
automatic model-prefix routing table (`orchestrator route` / `orchestrator
run` without an explicit `--provider`), because their model IDs are
ambiguous with another provider's:

- **Vertex AI** serves the exact same Gemini model ID strings as the
  native `gemini` provider (e.g. `gemini-2.5-pro` means the same thing to
  both) — an unresolvable string collision.
- **OCI** uses `vendor.model-name` IDs (`meta.llama-3.3-70b-instruct`,
  `xai.grok-4-fast-reasoning`) that share the `meta.` vendor prefix with
  Bedrock's own re-hosted model namespace.

Both must always be selected with an explicit `--provider vertexai` /
`--provider oci` (or `provider="vertexai"` / `provider="oci"` in the
Python API) — a bare model name will never auto-route to them.
