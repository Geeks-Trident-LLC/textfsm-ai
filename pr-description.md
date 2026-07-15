## Summary

This PR prepares the v0.5.1 release: two new CLI commands (`dsl` and
`pipeline`) exposing existing engine/pipeline functionality that previously
only had a Python API, plus small docs and test-hygiene fixes, following
v0.5.0.

## What's Included

### New CLI Commands
- `textfsm-ai dsl TEMPLATE_FILE SAMPLE_FILE` — deterministic template →
  canonical/readable/recognizer compilation, no LLM call. Same output-flag
  shape as `generate` (`--canonical`/`--readable`/`--recognizers`/
  `--sections`/`--json`)
- `textfsm-ai pipeline SAMPLE_FILE --provider ... --model ...` — the full
  sample → LLM-generated template → DSL-compiled output flow in one call,
  packaged per `--mode {quiet,default,info,debug}`, with `--json`. Reuses
  `generate`'s exact provider-resolution helpers (same credential
  precedence, same Bedrock/Vertex AI/OCI handling)
- Added missing `--help` text to `--provider`/`--api-key`/`--model`/
  `--endpoint`/`--api-version` on both `generate` and `pipeline`

### Documentation
- `docs/cli/index.md` — new `dsl` and `pipeline` sections
- `docs/providers/index.md` — mentions `textfsm-ai pipeline` as a CLI
  equivalent of `run_pipeline()`, alongside `textfsm-ai generate`

### Test Suite
- Silenced `cohere`'s internal `asyncio.iscoroutinefunction`
  `DeprecationWarning` (pinned dependency, not fixable at the source) —
  full suite now runs with 0 warnings, down from 78

## Release Artifacts
- CHANGELOG updated for v0.5.1
- Release notes generated
- Version bumped from 0.5.0 → 0.5.1

## Testing
- Full unit and integration suite passing (916 passed, 44 skipped, 0 warnings)
- `tox -e lint` clean
- TestPyPI release validated (`v0.5.1-test`)
