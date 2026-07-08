## v0.4.0 — 2026‑07‑08

### Added
- New template‑delivery pipeline with canonicalized rendering
- Recognizer and readable DSL renderers
- Unified GenerationController replacing legacy engines
- Full pricing engine with OpenAI, Azure, Anthropic, DeepSeek, Gemini support
- Longest‑prefix model family resolution
- Illegal dollar validator and expanded DSL syntax rules
- Full pytest suite for pricing

### Changed
- Updated provider model registry and CLI output modes
- Updated Azure provider endpoint handling
- Updated generation pipeline retry logic
- Updated AST parser with nested pattern/action support
- Updated CLI provider commands and integration tests

### Removed
- Legacy DSL engine and old generation pipeline
- Legacy delivery modules

### Fixed
- EndNode.textfsm_repr canonicalization bug
- Provider config defaults and Azure api_version mapping
