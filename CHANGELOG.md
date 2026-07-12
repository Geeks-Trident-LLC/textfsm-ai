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
