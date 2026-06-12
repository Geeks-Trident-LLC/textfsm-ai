## textfsm-ai v0.3.7

This release introduces the new **DSL Recognizer** subsystem, significantly improving the engine’s ability to infer generalized regex patterns from literal matched text.

### 🚀 New Features
- Added `_build_literal_regex()` with:
  - puncts‑group detection and recursion
  - improved tokenization rules
  - keyword‑aware literal generalization
  - fallback NUMBER pattern handling
- Added full test coverage:
  - literal regex builder tests
  - DSL recognizer tests
  - golden‑file snapshot tests

### 🧹 Maintenance
- Normalized line endings across the project
- Removed `.vscode/` from the repository and updated `.gitignore`

### 🔧 Internal
- Merged `feature/dsl-recognizer` into `develop`
- Version bump to `0.3.7`

This release lays the foundation for future DSL inference and recognizer improvements.
