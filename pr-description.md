## Summary

This PR prepares the v0.7.0 release: a `pip install -r ...`
alternative to the provider extras syntax, and removal of two features
judged out of scope for a template-generation tool (cost estimation,
model-tier classification), following v0.6.1. **Contains two breaking
changes** — see below.

## What's Included

### `requirements/` Alternative to Pip Extras (#65)
- `requirements-<provider>.txt` (SDK only, mirrors the matching
  `pyproject.toml` extra) and `dev-<provider>.txt` (`-e .[dev]` plus
  that provider's SDK, one-command local dev setup) for all 9 distinct
  provider SDKs
- No `requirements-all.txt`/`dev-all.txt` - `pip install
  textfsm-ai[all]` covers that
- Documented in `requirements/README.md`, `docs/getting-started/
  installation.md`, `CONTRIBUTING.md`

### Remove Cost/Pricing Estimation (#66)
- Deleted `core/pricing.py` + `pricing.yaml` entirely (432 lines,
  including a hardcoded-cutoff-date Claude Sonnet 5 pricing
  auto-updater)
- `delivery`'s `Usage` dataclass keeps only token counts + duration;
  drops `currency`/`estimated_cost`/`input_per_million`/
  `output_per_million`/`warning`
- `generate`'s `--usage` flag was already token-only, unaffected

### Drop Model Tier Classification (#67)
- Removed `tiers.py`, `patterns.py`, `classifier.py`,
  `curated-models.yaml` (~1,900 lines) - the `quality`/`balance`/
  `speed`/`thinking` taxonomy and the `list-models` filtering/
  `--latest` LLM-reclassification built on it
- `list-models <provider>` now always does a live fetch, no flags
- Kept: `model_catalog/providers.yaml` flattened to `{provider:
  default_model_id}`; `MODEL.<provider>.default` still resolves
  identically (verified against all 51 files that reference it)

## Breaking Changes

1. **`Usage`'s JSON/dict shape changes** (`--mode info/debug --json`,
   Python API's `DeliveryOutput`) - cost/pricing fields gone.
2. **`list-models` behavior changes** - always requires live provider
   credentials now; every filter flag and the credential-free curated
   fallback are gone.

Neither is part of the documented public-API stability contract
(`pricing`/`Usage`/tier fields never appeared in `api.py`/
`api_models.py`/`__init__.py`), but both are real, user-visible output/
CLI-behavior changes.

## Release Artifacts
- CHANGELOG updated for v0.7.0
- Release notes generated
- Version bumped from 0.6.1 → 0.7.0 (minor, given the two breaking
  changes)

## Testing
- Full unit and integration suite passing (876 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- TestPyPI release validated (`v0.7.0-test`)
