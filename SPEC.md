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
system is provider-agnostic: 18 LLM providers are supported, always
selected explicitly (`--provider anthropic`) — there is no auto-routing
or fallback between providers.

## 2. Layered architecture

```
┌───────────────────────────────────────────────────────────────────┐
│ CLI (textfsm_ai/cli/)          Public API (textfsm_ai/api.py)     │
├───────────────────────────────────────────────────────────────────┤
│ Delivery (textfsm_ai/delivery/)                                   │
│   chains generation + dsl, packages output per verbosity          │
├────────────────────────────────┬──────────────────────────────────┤
│ Generation                     │ DSL                              │
│ (textfsm_ai/generation/)       │ (textfsm_ai/dsl/)                │
│   sample -> LLM -> template    │   template -> AST ->             │
│   + records + validation       │   canonical/readable/            │
│                                │   recognizers                    │
├────────────────────────────────┴──────────────────────────────────┤
│ Providers (textfsm_ai/providers/)                                 │
│   delegates all LLM calls to the anyask package -                 │
│   no vendored provider SDK clients live in this repo              │
│ Model Catalog (textfsm_ai/model_catalog/)                         │
│   a default model ID per provider                                 │
└───────────────────────────────────────────────────────────────────┘
```

Each layer only depends on the ones below it. `generation/` and `dsl/`
don't depend on each other — `delivery/` is what wires them together.
There is no auto-routing/fallback layer: `generate`/`pipeline` always
resolve the provider explicitly via `--provider`, and the LLM call
itself is delegated to the [`anyask`](https://github.com/Geeks-Trident-LLC/anyask)
package rather than a layer this repo owns.

## 3. Provider system

`textfsm_ai/providers/` no longer implements any provider SDK client
itself — every actual LLM call goes through `anyask.ask(prompt, *,
provider, model, **kwargs)` (or `anyask.list_models()` for
`list-models`), a standalone package (same author, MIT) that owns the
18 provider implementations, its own `Provider` ABC, and its own
lazy-SDK-import registry. What's left in this repo is only what's
specific to *textfsm-ai as a tool*, not to *calling an LLM*:

- `providers/config.py` — CLI credential resolution
  (`load_config_from_file`/`load_config_from_env`, `ProvidersConfig`/
  `ProviderConfig`), independent of which library actually places the
  call. See §10.
- `generation/support/llm_extractor.py` — calls `anyask.ask()` and
  translates its typed `AskResponse` (or a raised
  `ProviderError`/`ProviderAuthError`/`ProviderNotFoundError`) into
  this repo's own `LLMRawResponse` shape, so the rest of the generation
  pipeline (§4) is unaware `anyask` exists at all.
- `generation/engine/generation_engine.py` — resolves
  `provider_name`/`model`/`api_key`/`endpoint`/`api_version`/
  `deployment`/`region`/`project`/`compartment_id` from CLI/env/config
  and forwards all of them unconditionally to `extractor.extract()`;
  `anyask.ask()`'s own construction-kwarg splitting picks out what each
  provider actually needs and ignores the rest, so there is no
  per-provider branching on this side either.

Every per-provider pip extra (`pip install textfsm-ai[anthropic]`, ...)
is a one-line pass-through to the matching `anyask[<provider>]` extra —
see §11.

### 3.1 Model catalog (`model_catalog/`)

Separate from the provider *code* is the provider *model catalog*:
- `providers.yaml` — a flat `{provider: default_model_id}` mapping; not
  a quality/speed opinion, just "a real, working model ID for this
  provider"
- `model_registry.py` / `__init__.py` — the `model.<provider>.default`
  facade used throughout the codebase and tests (e.g.
  `MODEL.groq.default`) instead of hardcoding raw model-ID strings
  everywhere

This package previously also included a `quality`/`balance`/`speed`/
`thinking` tier-classification system (`tiers.py`, `patterns.py`,
`classifier.py`, `curated-models.yaml`) backing `list-models`'
filtering and `--latest` LLM-based reclassification. Removed as
out-of-scope for a template-generation tool — "which model should I
use" is a model-selection-advisor concern, not parsing infrastructure,
unlike the plain default-model-ID mapping above (which is structural:
every provider class's constructor needs *some* fallback, and the test
suite needs *some* known-valid model ID to reference instead of
hardcoding strings everywhere).

This package was named `textfsm_ai/models/` before v0.6.1 — renamed to
`model_catalog` to disambiguate from the *data-model* dataclass files
described in §7 (`generation/core/models.py`, `dsl/core/models.py`,
`core/models.py`), which are an unrelated, conventional meaning of
"models."

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
    ├─ extractor.extract(provider_name, model, prompt)
    │     calls anyask.ask() (§3), wraps into LLMResponse
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
(§3.1):
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
(`generation/`, `dsl/`, `delivery/`, `providers/`, `model_catalog/`) is
internal implementation.

## 9. CLI surface (`textfsm_ai/cli/`)

`cli/top.py` assembles a `click` group from independently-defined
commands:

| Command | File | What it does |
|---|---|---|
| `generate` | `generate_cmd.py` | sample → LLM-generated template, many output-selection flags (`--template-only`, `--records`, `--explain`, `--handling`, `--sample`, `--raw`, `--usage`, `--sections`, `--json`, `--debug`) |
| `dsl` | `dsl_cmd.py` | template + sample → canonical/readable/recognizers, no LLM call |
| `pipeline` | `pipeline_cmd.py` | sample → LLM template → DSL compile, in one call, packaged per `--mode` |
| `list-models` | `list_models_cmd.py` | a provider's live models, via `anyask.list_models()` |
| `providers` | `providers_cmd.py` | `list`/`info`/`test` subcommands |
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

`ProvidersConfig` holds a `Dict[str, ProviderConfig]`
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

`pyproject.toml`'s base `dependencies` covers only the core CLI/API
(`PyYAML`, `requests`, `click`, `textfsm`) plus `anyask` itself — zero
provider SDKs. `anyask`'s own bare install pulls
only `PyYAML`, which this package already depends on unconditionally,
so adding it is +1 package (`anyask` itself) with zero new *transitive*
dependencies on a bare `pip install textfsm-ai` — verified via a real
clean-venv install.

Every provider is a `[project.optional-dependencies]` extra that's a
one-line pass-through to the matching `anyask` extra, e.g. `anthropic =
["anyask[anthropic]>=0.1.1"]` — `pip install textfsm-ai[anthropic]`
still works exactly as before, it now resolves `anyask[anthropic]`
(which pulls the real `anthropic` SDK) instead of pulling that SDK
directly. `[openai]` also covers the nine OpenAI-compatible providers
at no extra package cost (same as before); `[all]` pulls
`anyask[all]`, every provider SDK at once. This only works safely
because `anyask` does its own lazy SDK importing (§3) — without it,
importing `textfsm_ai` at all would require every SDK regardless of
which extra was installed. See `docs/guides/dependency-footprint.md`
for verified per-extra package counts.

Exact-version pins for individual provider SDKs (e.g. `mistralai`,
`boto3`, `cohere`, `oci`) are `anyask`'s concern now, not this
package's — see its own `pyproject.toml` for the current pins and
rationale.

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
- Generation-pipeline tests mock `anyask.ask()` directly (function
  boundary) rather than any HTTP/SDK layer — provider SDK behavior
  itself is `anyask`'s own test suite's responsibility, not this
  repo's.

## 13. Repository layout

```
textfsm_ai/
  api.py, api_models.py       — public API surface (§8)
  cli/                        — click commands (§9)
  core/                       — Serializable mixin, utils, ValidationResult
  providers/                  — CLI credential config, delegates LLM calls to anyask (§3)
  model_catalog/              — default model ID per provider (§3.1)
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
