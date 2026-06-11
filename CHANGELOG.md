## [0.3.4] - 2026-06-11
### Added
- Full DSL subsystem:
  - DSL node model (KeywordNode, QuantityNode, SequenceNode, etc.)
  - Canonicalization pipeline for stabilizing LLM-generated templates
  - DSL extractor for converting templates into DSL AST
  - DSL renderer for human-readable DSL output
  - DSL reverse parser with tokenizer-aware reconstruction
  - DSL inference for variable generalization and structural normalization

### Improved
- Added support for char/any/some/ws/wss keyword families
- Enhanced quantity-node semantics and generalization logic
- Improved literal-only transition handling in DSL renderer

### Refactored
- Removed unused and legacy DSL implementations
- Improved type annotations for full mypy compliance
- Applied ruff and black formatting across DSL modules

### Notes
- No breaking changes
- Engine and controller remain unchanged
- DSL integration into controller will be part of the next release
