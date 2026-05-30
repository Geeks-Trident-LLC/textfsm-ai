## What’s new in 0.1.3

### Fixes
- Removed unintended `__init__.py` at the project root that caused Python to treat the root folder as a package.
- Resolved mypy duplicate‑module error caused by conflicting import paths.

### Improvements
- Added `types-PyYAML` to ensure consistent type‑checking across local dev, tox, and CI.
- Cleaned and reorganized `requirements-dev.txt`.
- Updated `tox.ini` to include type stubs in the `typecheck` environment.

### Notes
This release contains no runtime or API changes. It focuses entirely on development tooling, type‑checking stability, and packaging correctness.
