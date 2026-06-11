## What’s new in v0.3.4

### 🚀 DSL Subsystem (Major Feature)
This release introduces the full TextFSM-AI DSL subsystem, providing a canonical,
machine-friendly, and human-friendly representation of generated templates.

Included components:
- DSL node model (KeywordNode, QuantityNode, SequenceNode, etc.)
- Canonicalization pipeline for stabilizing LLM-generated templates
- DSL extractor for converting templates → DSL AST
- DSL renderer for producing human-readable DSL
- DSL reverse parser with tokenizer-aware reconstruction
- DSL inference for variable generalization and structural normalization

### 🧹 Refactoring & Cleanup
- Removed legacy DSL implementations
- Improved type annotations for full mypy compliance
- Applied ruff + black formatting across the DSL modules

### 🛠 Internal Improvements
- Strengthened normalization logic for literal-only transitions
- Added support for char/any/some/ws/wss keyword families
- Improved quantity-node semantics and generalization rules

### 📦 No breaking changes
The engine and controller remain unchanged. DSL integration into the controller
will arrive in the next release.
