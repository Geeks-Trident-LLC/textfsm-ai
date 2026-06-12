## [0.3.7] - 2026-06-12

### Added
- Introduced the new DSL Recognizer subsystem:
  - Literal regex builder with puncts‑group recursion
  - Tokenizer improvements for whitespace, literal `\s+`, digits, punctuation, and fallback patterns
  - Full unit test suite for literal recognizer and DSL recognizer
  - Golden‑file tests for recognizer stability

### Changed
- Normalized line endings across the repository for consistency

### Removed
- Removed `.vscode/` directory from version control and added it to `.gitignore`

### Internal
- Merged `feature/dsl-recognizer` into `develop`
- Version bump: `0.3.6` → `0.3.7`
