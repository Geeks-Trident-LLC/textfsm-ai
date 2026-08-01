## Summary

This PR prepares the v0.6.1 release: documentation additions
(Dependency Footprint guide, SPEC.md) and internal cleanup (a package
rename to fix a naming collision, dead-code removal, config
consolidation), following v0.6.0.

## What's Included

### Documentation
- `docs/guides/dependency-footprint.md` (#59, #60) — verified
  per-provider `pip install textfsm-ai[<provider>]` package counts,
  from real clean-venv installs; wired into the docs nav and homepage
- `SPEC.md` (#64) — technical architecture reference: layered
  architecture diagram, provider system (lazy-loading registry, Shape
  A/B split, routing table), generation/DSL/delivery pipelines,
  data-model naming conventions, public API contract, CLI surface,
  configuration, v0.6.0 packaging model, testing conventions

### Internal Cleanup
- `textfsm_ai/models/` → `textfsm_ai/model_catalog/` (#63) — fixes a
  naming collision with the conventional data-model meaning already
  used by three other `models.py` files in the codebase; mechanical
  rename across 55 files, purely internal (never part of the public
  API)
- Removed `textfsm_ai/quota_manager.py` (#61) — dead code, never wired
  into any real call path
- Merged `mypy.ini` into `pyproject.toml`'s `[tool.mypy]` (#62) —
  matches the `pytest.ini` consolidation precedent from v0.4.1

## Release Artifacts
- CHANGELOG updated for v0.6.1
- Release notes generated
- Version bumped from 0.6.0 → 0.6.1 (patch — no breaking changes, all
  internal/docs)

## Testing
- Full unit and integration suite passing (926 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- TestPyPI release validated (`v0.6.1-test`)
