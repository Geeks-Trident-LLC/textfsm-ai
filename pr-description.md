## Summary

This PR fixes a packaging and type‑checking issue caused by an unintended
`__init__.py` at the project root (`textfsm-ai/`). Python treated the project
root as a package, which resulted in duplicate module paths during mypy runs.

## Changes

### Fixed
- Removed root-level `__init__.py` to prevent invalid package resolution.
- Resolved mypy error: “Source file found twice under different module names”.

### Added
- Added `types-PyYAML` to dev and tox type‑checking dependencies.

### Improved
- Cleaned and reorganized `requirements-dev.txt`.
- Updated `tox.ini` to ensure consistent type‑checking behavior.

## Impact

- No runtime or API changes.
- Development, CI, and packaging workflows are now stable and consistent.
