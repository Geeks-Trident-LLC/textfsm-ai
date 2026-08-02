## v0.7.1 — 2026‑08‑02

### Fixed
- **Token usage was undercounted**: `--mode info/debug` and `generate
  --usage` reported only the last generation attempt's token counts,
  silently dropping every prior base-prompt attempt and
  correction-prompt retry — each of which is a real, billed LLM
  call. `Usage` now sums `input_tokens`/`output_tokens`/
  `total_tokens`/`llm_duration_ms` across every attempt and gains a
  `calls` field (total LLM calls actually made). `default` mode is
  unaffected (no usage shown there); `debug` mode's per-stage raw
  pipeline breakdown was already accurate and is unchanged.

## v0.7.0 — 2026‑08‑02

### Added
- `requirements/requirements-<provider>.txt` and `requirements/
  dev-<provider>.txt` — a `pip install -r ...` alternative to the
  `pip install textfsm-ai[<provider>]` extras syntax, for pinned
  lockfiles, Docker layer caching, or tooling built around `-r` flags.
  One SDK-only file and one one-command-dev-setup file (`-e .[dev]`
  plus that provider's SDK) per provider. See `requirements/README.md`

### Changed
- **Breaking:** removed cost/pricing estimation entirely
  (`core/pricing.py`, `pricing.yaml`, including the Claude Sonnet 5
  introductory-pricing auto-update mechanism). `delivery`'s `Usage`
  dataclass (visible via `--mode info/debug`) drops `currency`/
  `estimated_cost`/`input_per_million`/`output_per_million`/`warning`,
  keeping only the factual token counts and duration. Maintaining a
  per-provider, per-model price table across 18 providers is
  disproportionate upkeep for a template-generation tool and belongs
  to dedicated cost-tracking tooling instead.
- **Breaking:** `list-models` no longer has curated/`--latest`/filter
  modes — it now always fetches a provider's live models directly
  (requires that provider's credentials, same as `generate`).
  `--latest`, `--latest-raw`, `--premium`, `--no-premium`, `--quality`,
  `--balance`, `--speed` are all removed, along with the
  `quality-chat`/`balance-chat`/`speed-chat`/`thinking-chat` tier
  taxonomy that backed them (`model_catalog/tiers.py`, `patterns.py`,
  `classifier.py`, `curated-models.yaml`) — "which model should I use"
  is a model-selection-advisor concern, not parsing infrastructure.
  Per-provider default model IDs (`MODEL.<provider>.default`,
  `pyproject.toml`-adjacent `providers.yaml`) are kept unchanged - that
  part is structural (every provider's constructor default, and the
  test suite's model-ID references), not advisory.

### Removed
- `textfsm_ai/core/pricing.py`, `pricing.yaml`
- `textfsm_ai/model_catalog/tiers.py`, `patterns.py`, `classifier.py`,
  `curated-models.yaml`

## v0.6.1 — 2026‑08‑01

### Added
- `docs/guides/dependency-footprint.md` — a verified, per-provider
  breakdown of exactly how many packages `pip install
  textfsm-ai[<provider>]` installs (14-34 depending on the provider),
  based on real clean-venv installs rather than reading
  `pyproject.toml` alone
- `SPEC.md` — a repo-root technical architecture reference covering the
  layered architecture, provider system, generation/DSL/delivery
  pipelines, data-model conventions, public API contract, CLI surface,
  configuration, packaging, and testing conventions

### Changed
- Renamed `textfsm_ai/models/` to `textfsm_ai/model_catalog/` (and its
  test directory to match) — the old name collided with the
  conventional data-model meaning already used by `core/models.py`,
  `generation/core/models.py`, and `dsl/core/models.py` (all dataclass
  files), when this package is actually about LLM model
  catalog/classification. Purely internal; not part of the public API
- Consolidated `mypy.ini` into `pyproject.toml`'s `[tool.mypy]`,
  matching the precedent already set for `pytest.ini`

### Removed
- `textfsm_ai/quota_manager.py` and its test — dead code for an "APC
  architecture" that no longer exists anywhere else in the codebase;
  nothing wired it into the orchestrator, providers, or CLI

## v0.6.0 — 2026‑07‑31

### Added
- Provider SDKs are now optional pip extras: `pip install textfsm-ai[anthropic]`,
  `[openai]` (also covers `deepseek`/`groq`/`xai`/`together`/`fireworks`/
  `cerebras`/`perplexity`/`openrouter`/`moonshot` - all OpenAI-compatible,
  share the `openai` package), `[gemini]`, `[vertexai]`, `[azure]`,
  `[mistral]`, `[bedrock]`, `[cohere]`, `[oci]`, or `[all]` for every
  provider SDK at once. `oci` alone (~36MB plus transitive crypto libs)
  is now fully opt-in instead of bundled unconditionally.
- Provider SDK imports are now lazy (`textfsm_ai/providers/registry.py`)
  — a missing SDK raises a clear `ImportError` pointing at the right
  extra (e.g. `pip install textfsm-ai[bedrock]`) only when that
  provider is actually used, instead of failing at package-import time
  regardless of which provider is needed.

### Changed
- **Breaking:** `pip install textfsm-ai` now installs only the core
  CLI/API (`PyYAML`, `requests`, `click`, `textfsm`) — no provider SDK.
  Previously every provider worked out of the box. Add the extra(s) you
  need on upgrade, e.g. `pip install textfsm-ai[anthropic]`, or
  `textfsm-ai[all]` for the old bundle-everything behavior.
- **Breaking:** the `all` extra now means "every provider SDK" (matching
  the new per-provider extras), not "dev + build tooling" as before —
  `dev`/`build` are still their own separate extras. `pip install -e
  ".[all,dev]"` is the new "everything for local development" command.
- Retired `requirements.txt`/`requirements-dev.txt` (already drifted
  from `pyproject.toml`, only ever consumed by one CI job) in favor of
  `pyproject.toml` extras as the single source of truth.

### Fixed
- `providers/__init__.py` no longer re-exports the `registry` singleton,
  which was silently shadowing the `registry` submodule at the package-
  attribute level (`import textfsm_ai.providers.registry as x` — and any
  other dotted-attribute resolution — would resolve to the singleton
  instance instead of the module). Latent bug, present before this
  release; never triggered until lazy-loading tests exercised it.

## v0.5.2 — 2026‑07‑31

### Added
- New `check_pattern_boundary_whitespace()` validator check, wired into
  `find_template_issues()` — flags a rule pattern ending in `\s+`/`\s+$$`
  (suggesting `\s*`/`\s*$$` instead) or starting with `^\s+` (suggesting
  `^\s*` instead), since `\s+` at a pattern boundary rejects lines where
  the whitespace happens to be absent
- New **Date/time variable names** rule in the LLM generation prompt
  (`prompts.yaml`) establishing a canonical vocabulary: `datetime`/`date`/
  `time` for single-field captures, `weekday`/`month`/`day`/`year`/`hour`/
  `minute`/`second`/`am_pm`/`timezone` for separate-field captures
  (`timezone` covers any representation — `PDT`, `+08:00`, `Z`, etc.) —
  so generated templates use consistent field names instead of ad hoc
  synonyms (`dow` vs `weekday`, `tz` vs `timezone`)

## v0.5.1 — 2026‑07‑15

### Added
- New `textfsm-ai dsl TEMPLATE_FILE SAMPLE_FILE` CLI command — deterministically
  compiles a TextFSM template into its canonical form, readable DSL, and
  recognizer patterns, with no LLM call made. Mirrors `generate`'s
  output-flag conventions (`--canonical`/`--readable`/`--recognizers`/
  `--sections`/`--json`)
- New `textfsm-ai pipeline SAMPLE_FILE --provider ... --model ...` CLI
  command — exposes the existing `DeliveryController`/`run_pipeline()`
  end-to-end flow (LLM generation + DSL compile, one call) directly via the
  CLI, with `--mode {quiet,default,info,debug}` and `--json` output; reuses
  `generate`'s provider-resolution helpers for identical credential handling
- `--help` text for `--provider`/`--api-key`/`--model`/`--endpoint`/
  `--api-version` on both `generate` and `pipeline` (previously undocumented
  on both)

### Changed
- `docs/providers/index.md` now mentions `textfsm-ai pipeline` alongside
  `textfsm-ai generate` as a CLI equivalent of `run_pipeline()`

### Fixed
- Silenced `cohere` SDK's internal `DeprecationWarning`
  (`asyncio.iscoroutinefunction`) in the test suite — third-party noise from
  a version pinned exactly for Python 3.9 CI compatibility, not something
  fixable at the source; eliminates all 78 warnings from a full suite run

## v0.5.0 — 2026‑07‑14

### Added
- Oracle Cloud Infrastructure (OCI) Generative AI provider (`provider="oci"`) —
  Meta Llama and xAI Grok models via OCI's Generic chat format, authenticated
  via `~/.oci/config` (no project-level API key); new `compartment_id`
  parameter / `--compartment-id` CLI flag; deliberately excluded from
  auto-routing (its `meta.`/`xai.` model-ID prefixes collide with Bedrock's
  re-hosted namespace)
- `docs/providers/index.md` — single overview page listing all 18 providers,
  their credentials, extra parameters, and Shape A/B and routing-collision
  notes
- Session-scoped SSL-context caching for the unit test suite
  (`tests/unit/conftest.py`) — cuts full suite runtime from 60+s to ~15-20s
  by eliminating redundant CA-bundle re-parsing on every real SDK client
  construction

### Changed
- **Breaking:** standardized every provider's environment variable naming to
  `<PROVIDER>_<FIELD>` with no exceptions: `AZURE_OPENAI_API_KEY` /
  `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_VERSION` /
  `AZURE_OPENAI_DEPLOYMENT` → `AZURE_API_KEY` / `AZURE_ENDPOINT` /
  `AZURE_API_VERSION` / `AZURE_DEPLOYMENT`; `AWS_REGION` /
  `AWS_DEFAULT_REGION` → `BEDROCK_REGION` / `BEDROCK_DEFAULT_REGION`;
  `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` → `VERTEXAI_PROJECT` /
  `VERTEXAI_REGION`. Update any scripts/CI/deployment configs that set the
  old names.
- `docs/index.md` homepage intro now correctly describes the AI-powered
  template-generation angle (previously read like a generic TextFSM parsing
  library with no mention of LLM generation); removed the false "Zero
  external dependencies" claim; replaced the redundant
  Documentation/Installation sections with a single "Explore the Docs"
  links section

### Removed
- `tests/unit/test_providers.py` and `tests/unit/test_providers_openai_compat.py`
  — fully superseded by `tests/unit/providers/*.py`, zero coverage loss

### Fixed
- `orchestrator.py`'s retry-exhaustion re-raise path (when every candidate
  provider has exhausted all retries) is now covered by a test; file moves
  from 91% to 100% coverage

## v0.4.2 — 2026‑07‑13

### Added
- New standardized public Python API facade: `generate()`/`compile_dsl()`/`run_pipeline()`
  (verb functions, always return a full result object) plus a `to_llm_*`/`to_*` shortcut
  family with identical parameters, returning either a single field or (for string-typed
  shortcuts) the failure reason on failure
- New `LLMResult`/`DSLResult` result dataclasses (`textfsm_ai/api_models.py`); `TemplateAST`,
  `DeliveryOutput`, and `ValidationResult` now also exported at the top level
- Quickstart guide, mkdocstrings-generated API Reference, a real CLI Guide, and a new
  Human-in-the-Loop Review guide (reviewing a generated template without reading regex)
- Test coverage raised to ~99% across nearly the entire codebase

### Changed
- Removed `ask_ai()`, the old raw single-provider-call primitive, superseded by
  `generate()`/`run_pipeline()`
- Removed broken/stale docs pages (`docs/providers/openai.md`, `docs/cli/providers-list.md`,
  `docs/golden-tests/`) describing unfinished scaffolding or a nonexistent golden-test framework

### Fixed
- `generate()` now sources `.ready`/`.reason` from the top-level generation pipeline (which
  accounts for retries and template-syntax validation) instead of the nested LLM response
  object (which only reflected whether the raw JSON had a template field) — the old logic
  could report success for a pipeline that had actually failed

## v0.4.1 — 2026‑07‑12

### Added
- `--version` CLI flag
- Comprehensive unit test coverage across the codebase (providers, delivery, DSL nodes, orchestrator, generation support, core utils) — overall coverage raised to ~95%
- CI workflow now also triggers on `develop` pushes, not just `main`

### Changed
- Split `dsl/core/nodes.py` into a `dsl/core/nodes/` package (`groups`, `base`, `leaf`, `modifiers`, `quantifiers`, `factory`) for maintainability; public import paths unchanged
- Reconciled packaging/build tooling: consolidated pytest config into `pyproject.toml` (removed a shadowing `pytest.ini`), fixed Makefile recipe tabs, aligned `pre-commit` hooks with pinned `tox` lint/format/typecheck versions

### Fixed
- `orchestrator/factory.py`: unreachable error branch for unknown provider types now correctly raises `ValueError` instead of relying on dead code that could never execute
- `generate_cmd.py`: incorrect `pconf.api_key` attribute reference and wrong `GEMINI_API_KEY` env var mapping

### Removed
- Confirmed dead code identified during a coverage audit (two cleanup passes)

## v0.4.0 — 2026‑07‑08

### Added
- New template‑delivery pipeline with canonicalized rendering
- Recognizer and readable DSL renderers
- Unified GenerationController replacing legacy engines
- Full pricing engine with OpenAI, Azure, Anthropic, DeepSeek, Gemini support
- Longest‑prefix model family resolution
- Illegal dollar validator and expanded DSL syntax rules
- Full pytest suite for pricing

### Changed
- Updated provider model registry and CLI output modes
- Updated Azure provider endpoint handling
- Updated generation pipeline retry logic
- Updated AST parser with nested pattern/action support
- Updated CLI provider commands and integration tests

### Removed
- Legacy DSL engine and old generation pipeline
- Legacy delivery modules

### Fixed
- EndNode.textfsm_repr canonicalization bug
- Provider config defaults and Azure api_version mapping
