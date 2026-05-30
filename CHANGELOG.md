# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog and Semantic Versioning.

---

## [0.1.3] - 2026-05-30
### Fixed
- Removed unintended `__init__.py` at project root (`textfsm-ai/`) that caused Python to treat the project root as a package and triggered mypy duplicate‑module errors.
- Resolved mypy error: “Source file found twice under different module names”.

### Added
- Added `types-PyYAML` to development and type‑checking dependencies for consistent stub availability across local, tox, and CI environments.

### Improved
- Cleaned and reorganized `requirements-dev.txt` for clarity and consistency.
- Updated `tox.ini` to include type stubs in the `typecheck` environment.
- Ensured type‑checking environment matches local development environment.

---

## [0.1.2] - 2026-05-27
### Fixed
- Corrected TestPyPI upload URL in CI workflow.

### Added
- Added release scripts and version verification tooling.
- Added tox configuration, scripts, and CI workflow.

### Improved
- Refactored CLI output model and version handling.
- Improved documentation structure and CLI docs.

---

## [0.1.1] - 2026-05-23
### Added
- Enabled documentation versioning with `mike`.
- Synced project version to 0.1.1.

---

## [0.1.0] - 2026-05-20
### Added
- Initial project structure, including:
  - AI router
  - Providers (Claude, DeepSeek, Gemini, OpenAI)
  - Quota manager
  - CLI commands
  - Config loader
  - Tests
  - Workflows
