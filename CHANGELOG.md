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
