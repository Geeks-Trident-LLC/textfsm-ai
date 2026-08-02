# textfsm-ai — Technical Architecture Spec

Version: tracks the codebase at `v0.6.0`. This document describes how the
system is built, not how to use it — see [README.md](README.md) and
`docs/` (built at
https://geeks-trident-llc.github.io/textfsm-ai/latest/) for the
user-facing guide, quickstart, and CLI reference.

## 1. What this system does

`textfsm-ai` turns raw, semi-structured text (CLI output, log lines) into
a validated TextFSM template, in one of two ways:

1. **LLM-generated**: send the sample to an LLM provider with a
   constrained prompt describing TextFSM's `Value`/`Rule` grammar; the
   model returns a template, parsed records, per-variable explanations,
   and notes on how it handled ambiguous lines. If the result fails
   validation, an automatic correction-prompt retry loop feeds the
   specific validation findings back to the model.
2. **Deterministic compile**: given any valid TextFSM template (LLM-authored
   or hand-written) plus example records, compile it into a canonical
   (regex-expanded) form, a human-readable DSL form, and recognizer
   patterns — no LLM call involved.

These two steps can be run independently or chained end to end. The
system is provider-agnostic: 18 LLM providers are supported behind one
interface, selected either explicitly (`--provider anthropic`) or by
automatic model-name routing.

## 2. Layered architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ CLI (textfsm_ai/cli/)          Public API (textfsm_ai/api.py)   │
├─────────────────────────────────────────────────────────────────┤
│ Delivery (textfsm_ai/delivery/)                                 │
│   chains generation + dsl, packages output per verbosity        │
├────────────────────────────────┬────────────────────────────────┤
│ Generation                     │ DSL                            │
│ (textfsm_ai/generation/)       │ (textfsm_ai/dsl/)              │
│   sample -> LLM -> template    │   template -> AST ->           │
│   + records + validation       │   canonical/readable/          │
│                                │   recognizers                  │
├────────────────────────────────┴────────────────────────────────┤
│ Orchestrator (textfsm_ai/orchestrator/)                         │
│   auto-routes a model name to a provider, retries/fallback      │
├─────────────────────────────────────────────────────────────────┤
│ Providers (textfsm_ai/providers/)                               │
│ Model Catalog (textfsm_ai/model_catalog/)                       │
│   one class per LLM provider, lazily imported;                  │
│   curated model lists, tier classification                      │
└─────────────────────────────────────────────────────────────────┘
```

Each layer only depends on the ones below it. `generation/` and `dsl/`
don't depend on each other — `delivery/` is what wires them together.
`orchestrator/` is a separate, parallel entry point (auto-routing a bare
model name to a provider) used by `textfsm-ai orchestrator route/run`
and `providers test`, not by the `generate`/`pipeline` path, which
always resolves the provider explicitly via `--provider`.

## 3. Provider system

### 3.1 `Provider` interface (`orchestrator/provider.py`)

An abstract base class every provider implements:
- `name: str` — class attribute, the provider's registry key
- `async generate(prompt, *, model, **kwargs) -> dict`
- `generate_sync(prompt, *, model, **kwargs) -> dict`
- `supports(model: str) -> bool`
- `from_env() -> Provider` (classmethod)

### 3.2 Registry and lazy loading (`providers/registry.py`)

`ProviderRegistry` holds a static map of
`{provider_name: (module_path, class_name, pip_extra)}` for all 19
registered names (18 providers + `openai_compat`, the shared
OpenAI-compatible base class). `registry.get(name)` only calls
`importlib.import_module()` — and thus only imports that provider's SDK
— the first time that specific name is requested, caching the resolved
class afterward. A missing SDK raises a clear `ImportError` naming the
correct `pip install textfsm-ai[<extra>]`.

This means `import textfsm_ai` and building the registry never require
any provider SDK to be installed; only *using* a specific provider does.
See `docs/guides/dependency-footprint.md` for the exact package cost per
extra.

### 3.3 Two provider shapes

- **Shape A ("OpenAI-compatible")** — `deepseek`, `groq`, `xai`,
  `together`, `fireworks`, `cerebras`, `perplexity`, `openrouter`,
  `moonshot` all subclass `OpenAICompatProvider`
  (`providers/openai_compat_provider.py`), which wraps the `openai`
  SDK's client pointed at a different `base_url`. No SDK of their own —
  the `[openai]` pip extra covers all nine.
- **Shape B ("native SDK")** — `openai`, `anthropic`, `gemini`,
  `vertexai`, `azure`, `mistral`, `bedrock`, `cohere`, `oci` each have
  their own provider file with custom `generate()`/`generate_sync()`
  logic mapping to that SDK's actual request/response shape.

Most providers construct with just `(api_key, model)`. Four need more:
`azure` (`api_key, endpoint, api_version, model`), `bedrock`
(`region, model`), `vertexai` (`project, region, model`), `oci`
(`compartment_id, region, model`). This shaping is hardcoded in
`generation/engine/generation_engine.py`'s `run()`/
`run_correction_prompt()` via an `if provider_type.name == ...` chain,
not something the `Provider` interface abstracts — a new provider
needing extra constructor params must be added there explicitly.

### 3.4 Model catalog (`model_catalog/`)

Separate from the provider *code* is the provider *model catalog*:
- `providers.yaml` / `curated-models.yaml` — per-provider model lists,
  grouped into tiers
- `tiers.py` — the `Tier` enum: `quality-chat`, `balance-chat`,
  `speed-chat`, `thinking-chat`, `other`
- `patterns.py` + `classifier.py` — regex patterns and classification
  logic that sort a raw model-name string (fetched live from a
  provider's API) into a tier
- `model_registry.py` / `__init__.py` — the `model.<provider>.<tier>.chat`
  facade used throughout the codebase and tests (e.g.
  `MODEL.groq.default`)

This package was named `textfsm_ai/models/` before v0.6.1 — renamed to
`model_catalog` to disambiguate from the *data-model* dataclass files
described in §7 (`generation/core/models.py`, `dsl/core/models.py`,
`core/models.py`), which are an unrelated, conventional meaning of
"models."

### 3.5 Orchestrator routing (`orchestrator/routing.py`)

`RoutingTable` maps a model-name *prefix* to a provider name via an
ordered list of `RoutingRule(prefix, provider_name)`, checked
first-match (not longest-prefix-match — ordering matters, and is
extensively commented in the source for every provider that required
non-obvious rule placement due to open-weight-model catalog overlaps).
`Orchestrator.run()` uses `route()` (no fallback) for the primary
provider, then also tries any other configured provider whose
`supports(model)` returns `True`, retrying on
`ProviderRateLimitError`/`ProviderTimeoutError`.

`vertexai` and `oci` are deliberately excluded from the routing table
entirely — `vertexai` serves identical Gemini model IDs to the native
`gemini` provider (no distinguishing prefix is possible), and `oci`'s
`meta.`/`xai.` vendor prefixes collide with Bedrock's own re-hosted
namespace. Both must always be selected via explicit `--provider`.

## 4. Generation pipeline (`generation/`)

```
sample text
    │
    ▼
GenerationController.run(sample)
    │  (up to max_retries attempts)
    ▼
generation_engine.run(provider_name, api_key, model, sample, ...)
    │
    ├─ prompt_builder.PromptBuilder().base_prompt(sample)
    │     reads generation/core/prompts.yaml's `base` template
    │
    ├─ extractor.extract(provider, model, prompt)
    │     calls provider.generate_sync(), wraps into LLMResponse
    │     (timing, token usage, raw payload)
    │
    ├─ structured_extractor.extract(response)
    │     strips ```json fences, json.loads(), validates the four
    │     expected fields (template/records/variables/handling) into
    │     StructuredResponse
    │
    └─ generator.generate(structured)
          runs validate_template_and_records() (generation/support/
          validator.py) — compiles the template with the real textfsm
          library and compares parsed records against what the LLM
          claimed — producing a GenerationStage(template, records,
          metadata, ready, reason)
    │
    ▼
if not ready: generation_engine.run_correction_prompt(..., prev_result)
    │
    ├─ validator.find_template_issues(template, records, sample)
    │     runs the FULL diagnostic battery (see §4.1) and joins every
    │     finding into a single reason string
    │
    └─ prompt_builder.correction_prompt(sample, prev_response, findings)
          embeds {base} + the previous JSON + the findings list into
          generation/core/prompts.yaml's `correction` template
    │
    ▼
GenerationPipeline(stages=[...], last_stage, ready, reason, attempts)
```

Retries happen twice over: `max_retries` attempts of the base prompt,
then (if none succeeded and the failure was structural rather than a
retryable provider error) `max_retries` attempts of the correction
prompt, each seeded with the specific validation findings from the
previous attempt.

### 4.1 Template validation (`generation/support/validator.py`)

Two entry points:
- `validate_template_and_records(template, sample, expected_records)` —
  compiles the template with the real `textfsm` library, parses the
  sample, and diff-checks the result against what the LLM claimed
  (row count, keys, values, variable-name casing). Used during the base
  generation attempt to decide `ready`.
- `find_template_issues(template, records, sample)` — if the above
  didn't pass, runs a battery of structural checks and returns every
  finding as a list of strings, each anchored to a stable code
  (`invalid_value_definition`, `missing_start_state`,
  `forbidden_state_name`, `illegal_dollar`, `invalid_rule_definition`,
  `inconsistent_rule_definition_spacers`,
  `pattern_trailing_whitespace_plus`, `pattern_leading_whitespace_plus`,
  etc.). These checks only run when something's already broken — a
  template that already validates cleanly returns no findings, even if
  it happens to violate a style rule.

`generation/core/prompts.yaml`'s `base` template is the single source
of truth for the grammar rules the LLM is asked to follow (`Value`
syntax, allowed rule forms, the `$$`-vs-bare-`$` rule, date/time
variable-naming conventions, etc.) — `validator.py`'s checks exist to
catch and correct violations of those same rules, not to define a
separate grammar.

## 5. DSL engine (`dsl/`)

```
raw TextFSM template + example records
    │
    ▼
dsl_engine.run(raw_template, records)
    │
    ├─ 1. ast.parser.parse_textfsm(template, records) → TemplateAST
    │       a purpose-built, more permissive parser than the real
    │       textfsm library (e.g. tolerates `Continue` combined with a
    │       state transition, which real textfsm rejects) — infers each
    │       Value's base type (word/digit/ip/number/...) from the
    │       example records via infer_base_keyword()
    │
    ├─ 2. render_template(ast, canonicalized=True) → canonical string
    │       regex-expands every inferred keyword/spacer into its full
    │       TextFSM-native regex form
    │
    ├─ 3. render_readable(ast) → human-readable DSL string
    │       e.g. `start() foo word(var-v1, options-Required) -> Record`
    │       — not TextFSM, a separate presentation the DSL engine
    │       invented for human review (see docs/guides/
    │       human-in-the-loop-review.md)
    │
    └─ 4. render_recognizer(ast) → List[str] of regex patterns
            one per rule, used to detect which template a block of text
            matches before actually parsing it
    │
    ▼
DSLParseResult(raw_template, records, ast, canonical, readable,
               recognizers, ready, reason)
```

Each of the four stages can fail independently; `DSLParseResult.name`
records which stage was in progress at failure, and `.reason` carries
the wrapped exception. `DSLController.run(gen: GenerationPipeline)` is
the adapter that feeds a `GenerationPipeline`'s last stage into this
engine, producing a `DSLPipeline`.

### 5.1 AST node types (`dsl/ast/nodes.py`)

`TemplateAST` = `values: List[ValueNode]` + `states: List[StateNode]`.
Each `StateNode` holds `rules: List[RuleNode]`, each `RuleNode` holds a
`PatternNode` (a list of `PatternItem` subclasses — `StartNode`,
`EndNode`, `SpacerNode`, `LiteralNode`, `CallNode`, `VarNode`, each
carrying `raw`/`textfsm_repr`/`expression`/`regex`) plus a list of
`Action` (line action, record action, target state, or the special
`Error`/`EOF` forms).

### 5.2 Core node/pattern machinery (`dsl/core/`)

`nodes/` (`base.py`, `leaf.py`, `groups.py`, `modifiers.py`,
`quantifiers.py`, `factory.py`) implements the actual keyword→regex
generation (`word`, `digit`, `ip`, `number`, etc., with
`generalize=True` producing the loosest safe pattern). `patterns.py`
holds the named base regex fragments (e.g. `puncts-group`).
`category_matcher.py` and `categories.py` support keyword inference from
example values.

## 6. Delivery pipeline (`delivery/`)

The end-to-end "do both steps in one call" path, exposed as
`run_pipeline()` in the public API and `textfsm-ai pipeline` on the CLI.

```
DeliveryController(provider_name, api_key, model, ...).run(sample, mode, as_json)
    │
    ├─ GenerationController.run(sample)         → GenerationPipeline
    ├─ DSLController.run(generation_pipeline)   → DSLPipeline
    │
    ▼
DeliveryEngine.assemble(mode, model_info, generation_pipeline,
                         dsl_pipeline, duration_ms, as_json)
    │
    └─ assembly/builder.build_delivery_package(...)
          assembles ALL FOUR verbosity views at once from the same
          underlying data (see delivery/core/package.py's dataclasses:
          Quiet, Default, Info, Debug), then DeliveryEngine picks which
          one to return based on `mode`
    │
    ▼
DeliveryOutput(mode, output: str, passed: bool, error: str)
```

Modes (`delivery/core/modes.py`'s `DeliveryMode` enum), each strictly a
superset of the previous:
- `quiet` — canonical template only, or a formatted failure/status block
- `default` — adds readable DSL + recognizers (`Output` dataclass)
- `info` — adds version info, masked LLM config, token usage, and the
  LLM's structured response
- `debug` — adds the full raw `GenerationPipeline`/`DSLPipeline` JSON
  dumps

`--json` on any mode switches from the formatted-text `to_string()` to
the structured `to_json()` of that same dataclass.

## 7. Data model conventions

Every result/pipeline dataclass across the codebase inherits from
`core/serializable.py`'s `Serializable` mixin, giving it `.to_dict()`,
`.to_json()`, `.to_dot_dict()`, and `.from_dict()` for free via
`dataclasses.asdict()` plus recursive normalization (handles nested
dataclasses, enums, and known LLM SDK response objects).

Three separate files named `models.py` exist, each scoped to one
feature area and holding that area's own dataclasses — this is the
conventional "data model" meaning, distinct from `model_catalog/`
(§3.4):
- `core/models.py` — `ValidationResult`
- `generation/core/models.py` — `LLMRawResponse`, `LLMResponse`,
  `StructuredResponse`, `TemplateValidationResult`,
  `TemplateFindingResult`, `GenerationStage`, `GenerationPipeline`
- `dsl/core/models.py` — `DSLParseResult`, `DSLPipeline`

`delivery/core/package.py` holds its own dataclasses (`Version`,
`LLMInfo`, `LLMResponse`, `LLMStructuredResponse`, `Usage`, `Output`,
`Status`, `Quiet`, `Default`, `Info`, `Debug`, `DeliveryPackage`,
`DeliveryOutput`) — deliberately separate from `generation`/`dsl`'s
models since they're presentation-shaped, not pipeline-shaped.

## 8. Public Python API (`textfsm_ai/api.py`)

Every function follows one of two naming conventions:
- **verb functions** (`generate()`, `compile_dsl()`, `run_pipeline()`) —
  always return the full result dataclass, `.ready`/`.reason` populated
  whether the call succeeded or not. Never raise for an ordinary
  LLM/generation failure.
- **`to_*` shortcuts** (`to_llm_template()`, `to_llm_records()`,
  `to_canonical()`, `to_readable()`, `to_recognizers()`, `to_ast()`,
  etc.) — same parameters as the matching verb function, return just
  one field. String-typed shortcuts return the failure `.reason`
  instead of an empty string on failure, so they can't be used to
  distinguish "failed" from "the field genuinely equals this string"
  without calling the full verb function first.

`textfsm_ai/__init__.py` re-exports the full public surface —
`generate`, `compile_dsl`, `run_pipeline`, every `to_*` shortcut,
`parse_to_dicts`/`parse_to_lists`/`validate_template`
(`core/utils/template.py`, thin wrappers around the real `textfsm`
library), and the result types (`LLMResult`, `DSLResult`, `TemplateAST`,
`DeliveryOutput`, `ValidationResult`). This is the only part of the
package with a semver-stability contract; everything else
(`generation/`, `dsl/`, `delivery/`, `providers/`, `model_catalog/`,
`orchestrator/`) is internal implementation.

## 9. CLI surface (`textfsm_ai/cli/`)

`cli/top.py` assembles a `click` group from independently-defined
commands:

| Command | File | What it does |
|---|---|---|
| `generate` | `generate_cmd.py` | sample → LLM-generated template, many output-selection flags (`--template-only`, `--records`, `--explain`, `--handling`, `--sample`, `--raw`, `--usage`, `--sections`, `--json`, `--debug`) |
| `dsl` | `dsl_cmd.py` | template + sample → canonical/readable/recognizers, no LLM call |
| `pipeline` | `pipeline_cmd.py` | sample → LLM template → DSL compile, in one call, packaged per `--mode` |
| `list-models` | `list_models_cmd.py` | curated or live (`--latest`/`--latest-raw`) model list per provider, with tier filters |
| `providers` | `providers_cmd.py` | `list`/`info`/`test` subcommands |
| `orchestrator` | `orchestrator_cmd.py` | `route`/`run` subcommands — the auto-routing path (§3.5), distinct from `generate`/`pipeline`'s explicit `--provider` |
| `version` | `version_cmd.py` | prints `__version__` |

`generate` and `pipeline` share the exact same provider-credential
resolution helpers (`resolve_api_key`, `resolve_model`,
`resolve_endpoint`, `resolve_api_version`, `resolve_region`,
`resolve_project`, `resolve_compartment_id`, all defined once in
`generate_cmd.py` and imported by `pipeline_cmd.py`) — CLI flag >
provider-specific environment variable > `providers.yaml` precedence,
with Bedrock/Vertex AI/OCI's ambient-credential-chain exceptions
documented inline.

## 10. Configuration (`providers/config.py`)

`OrchestratorConfig` holds a `Dict[str, ProviderConfig]`
(`name`/`type`/`params`), sourced from two places, merged by the CLI
(env vars take precedence over the YAML file when both are present):
- `load_config_from_file(path="")` — defaults to
  `model_catalog/providers.yaml`, each provider's default model/params
- `load_config_from_env()` — one `if os.getenv(...)` branch per
  provider, building a `ProviderConfig` only for providers with their
  required env var(s) actually set

Every provider's env vars follow `<PROVIDER>_<FIELD>` uniformly (e.g.
`OPENAI_API_KEY`, `AZURE_ENDPOINT`, `BEDROCK_REGION`,
`VERTEXAI_PROJECT`, `OCI_COMPARTMENT_ID`) — standardized in v0.5.0 as a
deliberate breaking change from each SDK's own ecosystem-convention
naming.

## 11. Packaging & dependencies

Since v0.6.0, `pyproject.toml`'s base `dependencies` covers only the
core CLI/API (`PyYAML`, `requests`, `click`, `textfsm`, conditionally
`tomli`) — zero provider SDKs. Every provider is a
`[project.optional-dependencies]` extra
(`pip install textfsm-ai[anthropic]`, `[openai]` — also covers the nine
OpenAI-compatible providers at no extra package cost — `[gemini]`,
`[vertexai]`, `[azure]`, `[mistral]`, `[bedrock]`, `[cohere]`, `[oci]`,
or `[all]` for every provider). This only works safely because of the
lazy-loading registry (§3.2) — without it, importing `textfsm_ai` at all
would require every SDK regardless of which extra was installed. See
`docs/guides/dependency-footprint.md` for verified per-extra package
counts (14–34 packages depending on the provider's own SDK design).

Four provider SDKs are pinned to an exact version rather than a floor,
each because it's the last release still supporting this package's
`requires-python = ">=3.9"` floor: `mistralai==1.10.0`,
`boto3==1.42.97`, `cohere==5.21.1`. `oci==2.182.0` is pinned for
reproducibility rather than a 3.9 constraint (its latest release already
supports 3.9).

## 12. Testing conventions

- `tests/unit/` mirrors `textfsm_ai/`'s package structure 1:1.
- `tests/integration/` holds real-provider-call tests, gated behind a
  `@pytest.mark.integration` marker and a custom `--real` pytest flag
  (skipped by default; CI never runs them).
- `pyproject.toml`'s `[tool.pytest.ini_options]` enforces `fail_under =
  70` coverage; the actual suite runs at ~99%.
- `tox.ini` defines `py39`/`py312` (full suite via `extras = dev,all`),
  `lint` (ruff + black check), `format` (ruff + black, writes changes),
  `typecheck` (mypy, config lives in `pyproject.toml`'s `[tool.mypy]`),
  and `docs` (`mkdocs build --strict`).
- Provider tests mock at the HTTP boundary (`respx`, already a `dev`
  dependency) rather than mocking SDK client methods directly, to catch
  real request-shape regressions.

## 13. Repository layout

```
textfsm_ai/
  api.py, api_models.py       — public API surface (§8)
  cli/                        — click commands (§9)
  core/                       — Serializable mixin, utils, ValidationResult
  providers/                  — Provider implementations + registry (§3)
  model_catalog/              — model name → tier classification, curated lists (§3.4)
  orchestrator/                — auto-routing, retries (§3.5)
  generation/                  — sample → LLM → validated template (§4)
    core/                      — dataclasses + prompts.yaml
    engine/                    — the run()/run_correction_prompt() pipeline
    support/                   — extractor, structured_extractor, generator, validator, prompt_builder
    controller/                — GenerationController (retry loop)
  dsl/                         — template → AST → canonical/readable/recognizers (§5)
    ast/                       — parser + node types
    core/                      — dataclasses, node/pattern machinery
    engine/                    — dsl_engine.run() + render/*
    controller/                — DSLController
    support/                   — aliases
  delivery/                    — chains generation + dsl, verbosity packaging (§6)
    core/                      — package.py dataclasses, modes.py
    engine/, controller/, assembly/

tests/
  unit/                        — mirrors textfsm_ai/ 1:1
  integration/                 — real-provider tests, --real gated

docs/                          — mkdocs site (Installation, Quickstart,
                                  CLI Guide, Providers, Guides, API Reference)
```
