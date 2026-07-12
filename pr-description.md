## Summary

This PR prepares the v0.4.1 release: a maintainability and quality‑focused release
following v0.4.0, adding a `--version` CLI flag, refactoring the DSL node module into
a package, fixing a packaging/CI gap, and raising unit test coverage to ~95% across
nearly every module in the codebase.

## What's Included

### CLI
- New `--version` flag

### DSL
- `dsl/core/nodes.py` split into a `dsl/core/nodes/` package (`groups`, `base`, `leaf`,
  `modifiers`, `quantifiers`, `factory`) — no change to public import paths or behavior

### Packaging & CI
- Consolidated pytest configuration into `pyproject.toml` (removed a `pytest.ini` that
  was silently shadowing it, including coverage options)
- Fixed Makefile recipe tabs and aligned `pre-commit` hooks with pinned `tox`
  lint/format/typecheck versions
- CI workflow now also triggers on `develop` pushes, not just `main`

### Bug Fixes
- `orchestrator/factory.py`: unreachable error branch for unknown provider types now
  correctly raises `ValueError`
- `generate_cmd.py`: incorrect `pconf.api_key` attribute reference and wrong
  `GEMINI_API_KEY` env var mapping

### Test Coverage
- Added dedicated unit test suites for: all provider modules, delivery
  assembly/controller/engine, `dsl/core/nodes/factory.py`, `generation/support/llm_extractor.py`,
  `dsl/engine/dsl_engine.py`, `core/serializable.py`, `core/dotdict.py`,
  `core/utils/template.py`, and CLI/package coverage gaps
- Overall coverage raised from the low‑80s to ~95%

## Release Artifacts
- CHANGELOG updated for v0.4.1
- Release notes generated
- Version bumped from 0.4.0 → 0.4.1

## Testing
- Full unit and integration suite passing (562 passed, 18 skipped)
- `tox -e format,lint,typecheck` clean
- TestPyPI release validated (`v0.4.1-test`)
