## Summary

This PR introduces the new **DSL Recognizer** subsystem, including the literal regex builder, improved tokenization logic, and a comprehensive test suite. This feature enables the engine to generalize literal matched text into stable, reusable regex patterns.

## Key Changes

### ✨ New: DSL Recognizer
- Implemented `_build_literal_regex()` with:
  - puncts‑group recursion
  - whitespace normalization
  - literal `\s+` handling
  - digit and punctuation classification
  - fallback NUMBER pattern
- Added `_build_variable_pattern()` integration
- Added visualizers for literal → regex and pattern → match previews

### 🧪 Test Coverage
- Added `test_literal_regex.py` (unit tests)
- Added `test_dsl_recognizer.py` (integration tests)
- Added golden‑file snapshot tests for recognizer output

### 🧹 Cleanup
- Normalized line endings
- Removed `.vscode/` from repo and updated `.gitignore`

## Versioning
- Bumped version: `0.3.6` → `0.3.7`

## Notes
This PR is foundational for upcoming DSL inference improvements and recognizer stability work.
