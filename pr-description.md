## Summary

This PR promotes the v0.3.4 release from `develop` to `main`.  
The release introduces the complete DSL subsystem, enabling canonical template
generation, machine-DLS extraction, human-DLS rendering, and reverse parsing.

All release-test checks have passed, including:
- lint (ruff)
- format (black)
- typecheck (mypy)
- unit tests
- integration tests

## What’s Included in v0.3.4

### DSL Subsystem (Major Feature)
- Canonicalization pipeline for stabilizing LLM-generated templates
- DSL node model (KeywordNode, QuantityNode, SequenceNode, etc.)
- DSL extractor for template → DSL AST conversion
- DSL renderer for human-readable DSL output
- DSL reverse parser with tokenizer-aware reconstruction
- DSL inference for variable generalization and structural normalization

### Refactoring & Cleanup
- Removed unused and legacy DSL code
- Improved type annotations for mypy compliance
- Applied ruff + black formatting

### Internal Enhancements
- Literal-only transition support in renderer
- Expanded keyword families (char/any/some/ws/wss)
- Improved quantity-node semantics and generalization logic

## Release Notes
See `CHANGELOG.md` entry for v0.3.4.

## Version
Bumped version: `0.3.3 → 0.3.4`.

## Next Steps
- Integrate DSL canonicalization into the controller pipeline
- Prepare v0.3.5-dev branch after merge
