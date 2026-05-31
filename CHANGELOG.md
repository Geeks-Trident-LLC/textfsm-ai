## [0.1.20] - 2026-05-31
### Added
- Improved project banner (`banner.svg`) with enhanced text outline and alignment for better visual clarity.

### Fixed
- Updated PyPI publish workflow inputs to use kebab-case (`packages-dir`, `verify-metadata`) to match the GitHub Actions schema.
- Corrected PyPI trusted publishing configuration by removing legacy auth fields and switching to the proper `release/v1` action tag.

### Changed
- Updated `pyproject.toml` metadata and documentation links.
