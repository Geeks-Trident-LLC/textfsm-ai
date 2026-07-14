# CLI Guide

`textfsm-ai` installs a `textfsm-ai` command with subcommands for generating
templates, listing/inspecting providers, and driving the orchestrator
directly.

## Version

```bash
textfsm-ai --version
# or
textfsm-ai version
```

## generate

Generate a TextFSM template (and related output) from a sample, via an LLM
provider.

```bash
textfsm-ai generate sample.txt --provider openai --model gpt-4o-mini
```

Provider credentials are resolved in this order: CLI flag > provider-specific
environment variable (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `GROQ_API_KEY`, `XAI_API_KEY`,
`TOGETHER_API_KEY`, `FIREWORKS_API_KEY`, `CEREBRAS_API_KEY`,
`PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY`, `MOONSHOT_API_KEY`,
`MISTRAL_API_KEY`, `COHERE_API_KEY`, `AZURE_API_KEY`) > `providers.yaml`.

Azure additionally resolves `--model` (as the deployment name), `--endpoint`,
and `--api-version` from `AZURE_DEPLOYMENT`, `AZURE_ENDPOINT`, and
`AZURE_API_VERSION` the same way.

Bedrock, Vertex AI, and OCI are the exceptions to the credential rule
above: none of them has a project-level API key at all.

- Bedrock resolves `--region` from `BEDROCK_REGION`/`BEDROCK_DEFAULT_REGION`
  (or `providers.yaml`), and authenticates via boto3's own AWS credential
  chain (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_SESSION_TOKEN`,
  `~/.aws/credentials`, or an IAM role) — nothing AWS-secret-shaped ever
  passes through this CLI.
- Vertex AI resolves `--region` from `VERTEXAI_REGION` and `--project`
  from `VERTEXAI_PROJECT` (or `providers.yaml`), and authenticates via
  the `google-genai` SDK's own Application Default
  Credentials chain (a service account key file via
  `GOOGLE_APPLICATION_CREDENTIALS`, `gcloud auth application-default
  login`, or workload identity) — same principle, nothing GCP-secret-shaped
  passes through this CLI either. Vertex AI must always be selected with
  `--provider vertexai` explicitly — it serves the same Gemini models as
  the native `gemini` provider under identical model IDs, so there's no
  automatic way to route between the two.
- OCI resolves `--compartment-id` from `OCI_COMPARTMENT_ID` (or
  `providers.yaml`), and authenticates via the `oci` SDK's own config
  file at `~/.oci/config` (DEFAULT profile) — the same file the OCI CLI
  itself uses. `--region` is optional for OCI: unlike Bedrock/Vertex AI it
  falls back to whatever region is already set in `~/.oci/config` if not
  resolved from `--region`/`OCI_REGION`/`providers.yaml`. OCI must always
  be selected with `--provider oci` explicitly — its `meta.`/`xai.`
  model-ID vendor prefixes collide with Bedrock's own re-hosted namespace,
  so there's no automatic way to route between the two.

Key options:

| Option | Purpose |
|---|---|
| `--provider` (required) | Provider name: `openai`, `anthropic`, `gemini`, `deepseek`, `groq`, `xai`, `together`, `fireworks`, `cerebras`, `perplexity`, `openrouter`, `moonshot`, `mistral`, `bedrock`, `cohere`, `vertexai`, `oci`, `azure` |
| `--api-key` | Override the resolved API key (ignored for `bedrock`/`vertexai`/`oci`) |
| `--model` | Model name (or Azure deployment name) |
| `--endpoint`, `--api-version` | Azure-only |
| `--region` | AWS region (Bedrock), GCP location (Vertex AI), or OCI region (OCI, optional) |
| `--project` | GCP project (Vertex AI only) |
| `--compartment-id` | OCI compartment OCID (OCI only) |
| `--max-retries` | Retry attempts (default: 1) |
| `--template-only` | Print only the final TextFSM template |
| `--records` | Print parsed records |
| `--explain` | Print variable explanations |
| `--handling` | Print LLM notes on how it handled the sample |
| `--sample` | Print the input sample sent to the LLM |
| `--raw` | Print the raw LLM response |
| `--usage` | Print token usage |
| `--sections` | Print template, records, explanations, and handling together |
| `--json` | Print the full pipeline as JSON |
| `--debug` | Print resolved provider/model/api-key (masked) before running |

With no output flag, `generate` prints just the final template.

## list-models

List models for a provider — curated groups by default, or live data from the
provider's API.

```bash
textfsm-ai list-models openai
textfsm-ai list-models openai --latest       # fetch + LLM-classify into tiers
textfsm-ai list-models openai --latest-raw   # fetch without classification
textfsm-ai list-models openai --premium --quality
```

Filter flags: `--premium`, `--no-premium`, `--quality`, `--balance`, `--speed`.

## providers

```bash
textfsm-ai providers list
```
```text
NAME           DESCRIPTION
-------------  ----------------------------------------
anthropic      Anthropic Claude models
azure          Azure AI Inference / Azure OpenAI
bedrock        Amazon Bedrock (native SDK, AWS credential chain)
cerebras       Cerebras (fast open-model inference, OpenAI-compatible API)
cohere         Cohere Command models (native SDK)
deepseek       DeepSeek (OpenAI-compatible API)
fireworks      Fireworks AI (open-model hosting, OpenAI-compatible API)
gemini         Google Gemini models
groq           Groq (fast open-model inference, OpenAI-compatible API)
mistral        Mistral AI (native SDK)
moonshot       Moonshot AI / Kimi models (OpenAI-compatible API)
oci            Oracle Cloud Infrastructure Generative AI (Llama/Grok, config-file auth)
openai         Native OpenAI API
openai_compat
openrouter     OpenRouter (multi-provider model aggregator, OpenAI-compatible API)
perplexity     Perplexity (search-grounded Sonar models, OpenAI-compatible API)
together       Together AI (open-model hosting, OpenAI-compatible API)
vertexai       Google Vertex AI (Gemini via GCP, ADC credential chain)
xai            xAI Grok models (OpenAI-compatible API)
```

```bash
textfsm-ai providers info --name openai [--config path/to/config.yaml]
```
Prints the configured type and params for that provider, with sensitive keys
(`api_key`, `token`, `secret`, `password`-like) masked to `***`.

```bash
textfsm-ai providers test --model openai/gpt-4o-mini --prompt "Say hello" [--config path/to/config.yaml]
```
Sends a test prompt straight through the orchestrator to whichever provider
the model routes to, and prints the raw response.

## orchestrator

```bash
textfsm-ai orchestrator route --model claude-opus-4-8
```
```text
Model: claude-opus-4-8
Routed provider: anthropic
```
Shows which provider a model would route to, without making a real call.

```bash
textfsm-ai orchestrator run --model gpt-4o-mini --prompt "Say hello" [--config path/to/config.yaml]
```
Runs a full orchestrator request (routing + retries + provider call) and
prints the response.

## Next steps

- See the [Quickstart](../getting-started/quickstart.md) for the equivalent
  Python API.
- See the [API Reference](../reference/index.md) for every function and
  result type.
