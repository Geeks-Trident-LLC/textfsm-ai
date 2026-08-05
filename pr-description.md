## Summary

This PR prepares the v0.8.0 release: all 18 LLM provider
implementations are now delegated to the `anyask` package instead of
being vendored, and the unused `orchestrator/` auto-routing layer is
removed, following v0.7.1. Two internal-only breaking changes - no
`pip install`/CLI-facing breakage for typical users.

## What's Included

### Replace Vendored Providers with `anyask` (#69)
- All 18 provider implementations, the `Provider` ABC, and the
  lazy-SDK-import registry are now owned by
  [`anyask`](https://github.com/Geeks-Trident-LLC/anyask) (same author,
  MIT) - `textfsm-ai` calls `anyask.ask()`/`anyask.list_models()`
  instead of maintaining its own copy of the same code.
- `pip install textfsm-ai[<provider>]` is unchanged for end users -
  every extra is now a one-line pass-through to `anyask[<provider>]`.
  Verified via a real clean-venv install: `anyask` adds exactly +1
  package with zero new transitive dependencies.
- `generation/support/llm_extractor.py` translates `anyask`'s typed
  `AskResponse`/exceptions back into this repo's existing
  `LLMRawResponse` shape, so `extractor.py`, `structured_extractor.py`,
  `generation_controller.py`, and all of `delivery/` needed zero
  changes. `generation_engine.py`'s per-provider branching is gone
  entirely - every resolved field is forwarded unconditionally and
  `anyask.ask()` picks out what each provider needs.

### Remove `orchestrator/` (#69)
- Deleted `textfsm_ai/orchestrator/` and its CLI (`orchestrator
  route/run`) - confirmed unused by the real `generate`/`pipeline`
  path, which always resolves a provider explicitly via `--provider`.
  Duplicated `generate` while doing exactly the auto-routing/fallback
  `anyask` itself explicitly disclaims.
- `providers test` kept (provider connectivity smoke test), rewired to
  call `anyask.ask()` directly with a required `--provider` flag.

## Breaking Changes

1. **`textfsm_ai.orchestrator.*` and `textfsm_ai.providers.<x>_provider`
   modules are gone**, along with `OrchestratorConfig` (renamed
   `ProvidersConfig`). None were part of the documented public API
   (`textfsm_ai/__init__.py`/`api.py`), but real for anyone importing
   them directly.
2. **`providers test` requires `--provider`** instead of inferring the
   provider from a `"provider/model"`-shaped `--model` string.

Neither affects `pip install textfsm-ai[<provider>]`, `generate`,
`pipeline`, `dsl`, `list-models`, or `providers list/info` - all
unchanged for typical users.

## Release Artifacts
- CHANGELOG updated for v0.8.0
- Release notes generated
- Version bumped from 0.7.1 → 0.8.0 (minor, given the two
  internal-only breaking changes)

## Testing
- Full unit and integration suite passing (597 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- Real end-to-end CLI smoke tests (mocked `anyask.ask`/`list_models`):
  `generate`, `pipeline --mode info`, `providers list/test`,
  `list-models`
- Real clean-venv install verification (bare install and
  `[anthropic]`), plus a TestPyPI install (`v0.8.0-test`) confirming
  `anyask` resolves correctly from PyPI alongside the TestPyPI package
