## Summary

This PR prepares the v0.8.1 patch release: removes the redundant
`verify-version` scripts and refactors every remaining
`pyproject.toml`-version-reading spot to regex instead of
`tomllib`/`tomli`, following v0.8.0. No breaking changes.

## What's Included

### Remove Redundant `verify-version` Scripts
- `scripts/verify-version.py`/`.ps1` duplicated
  `tests/unit/test_version_consistency.py`, which already runs the
  same regex-based version-consistency check as a real pytest test in
  CI. Removed both, along with the now-dangling pre-commit hook
  (`.pre-commit-config.yaml`) and Makefile target (`verify-version`)
  that invoked `verify-version.py`.

### Refactor `tomllib`/`tomli` Usage to Regex
- `scripts/release.ps1`'s `Get-Version`, the `Makefile`'s
  `VERSION :=`, and the docs-deploy GitHub Actions workflow
  (`.github/workflows/docs.yml`) all read `pyproject.toml`'s version
  via `tomllib`/`tomli` - inconsistent with the regex approach already
  used by `verify-version.py`/`test_version_consistency.py`.
  Refactored all three to regex; `release.ps1` now uses PowerShell's
  native `-match` instead of shelling out to Python at all.
- Removed the now-unused conditional `tomli` dependency from
  `pyproject.toml` - nothing in `textfsm_ai`'s own source or tooling
  parses TOML anymore.

## Release Artifacts
- CHANGELOG updated for v0.8.1
- Release notes generated
- Version bumped from 0.8.0 → 0.8.1 (patch - tooling cleanup, no
  behavior change)

## Testing
- Full unit and integration suite passing (597 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- `mkdocs build --strict` clean
- Verified the refactored regex commands directly (Python one-liner
  and PowerShell `-match`) both correctly extract `0.8.1`
- `.pre-commit-config.yaml` validated as parseable YAML after the hook
  removal
- TestPyPI release validated (`v0.8.1-test`)
