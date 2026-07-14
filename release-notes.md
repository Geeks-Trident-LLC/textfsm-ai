# v0.5.0 — Oracle OCI Provider, Env Var Standardization, Faster Tests

## 🔮 New Provider: Oracle Cloud Infrastructure (OCI)
`textfsm_ai` now supports Oracle Cloud's Generative AI service
(`provider="oci"`):
- Meta Llama and xAI Grok models via OCI's Generic chat format
- No project-level API key — authenticates via `~/.oci/config` (the same
  file the OCI CLI itself uses), matching the credential-chain shape
  already used for Bedrock and Vertex AI
- New `compartment_id` parameter / `--compartment-id` CLI flag
- Always selected explicitly via `--provider oci` — its model-ID vendor
  prefixes collide with Bedrock's re-hosted namespace, so it's
  intentionally left out of automatic routing

## ⚠️ Breaking Change: Environment Variable Standardization
Every provider's environment variables now follow one uniform
`<PROVIDER>_<FIELD>` naming pattern:

| Old | New |
|---|---|
| `AZURE_OPENAI_API_KEY` | `AZURE_API_KEY` |
| `AZURE_OPENAI_ENDPOINT` | `AZURE_ENDPOINT` |
| `AZURE_OPENAI_API_VERSION` | `AZURE_API_VERSION` |
| `AZURE_OPENAI_DEPLOYMENT` | `AZURE_DEPLOYMENT` |
| `AWS_REGION` / `AWS_DEFAULT_REGION` | `BEDROCK_REGION` / `BEDROCK_DEFAULT_REGION` |
| `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` | `VERTEXAI_PROJECT` / `VERTEXAI_REGION` |

**If you have any of the old env var names set, update them before
upgrading** — the old names are no longer read.

## 📚 New Providers Overview Page
A single new doc page, **Providers**, lists all 18 supported providers
side by side: credentials, extra parameters, example models, and notes on
the internal Shape A/B split and routing collisions.

## 🏠 Refreshed Docs Homepage
The docs homepage now correctly leads with what `textfsm_ai` actually
is — an AI-powered template generator across 18 LLM providers — instead
of reading like a generic TextFSM parsing library. Also fixed a stale
"Zero external dependencies" claim (the package depends on `openai`,
`anthropic`, `google-genai`, `boto3`, `oci`, and more).

## 🧪 ~4x Faster Test Suite
- Removed two test files fully superseded by the per-provider test
  directory, with zero coverage loss
- Traced the bulk of the provider test suite's runtime to
  `ssl.create_default_context()` re-parsing the full CA certificate
  bundle on every real SDK client construction; caching it for the test
  session cuts the full suite from 60+ seconds to ~15-20 seconds
- Closed `orchestrator.py`'s one remaining coverage gap (the
  retry-exhaustion re-raise path) — now 100% covered

## 📦 Version
`0.4.2 → 0.5.0`
