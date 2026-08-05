# v0.8.1 — Dev-Tooling Cleanup

## 🧹 Internal: Version-Parsing Cleanup
No user-facing changes in this release - housekeeping on the
release/dev tooling only.

- Removed `scripts/verify-version.py`/`.ps1`, which duplicated a check
  already covered by a real pytest test
  (`tests/unit/test_version_consistency.py`) that runs in CI.
- Every remaining spot that read `pyproject.toml`'s version now uses
  regex instead of `tomllib`/`tomli`, and the now-unused conditional
  `tomli` dependency is gone.

## 📦 Version
`0.8.0 → 0.8.1`
