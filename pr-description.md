## Summary

This PR prepares the v0.4.0 release, introducing the new template‑delivery pipeline,
expanded DSL rendering capabilities, unified generation architecture, and the new
pricing engine with Azure/Anthropic/DeepSeek support.

## What’s Included

### Delivery & DSL
- Unified template‑delivery pipeline across DSL, generation, and orchestrator layers
- Canonicalized pattern rendering and improved EndNode handling
- New readable and recognizer renderers
- Updated AST parser with nested pattern/action support
- Illegal dollar validator and expanded syntax checks

### Generation & Providers
- New GenerationController replacing legacy engines
- Unified provider selection and retry logic
- Updated Azure provider integration and endpoint handling
- Expanded provider model registry and CLI output modes

### Pricing Engine
- New pricing subsystem with:
  - OpenAI, Azure, Anthropic, DeepSeek, Gemini pricing tables
  - Longest‑prefix model family resolution
  - Reasoning‑token billing
  - Sonnet‑5 auto‑update logic
- Full pytest suite for pricing

### CLI
- Updated `generate` command with advanced output modes
- Updated provider configuration and integration tests

## Release Artifacts
- CHANGELOG updated for v0.4.0
- Release notes generated
- Version bumped from 0.3.8 → 0.4.0

## Testing
- Full unit and integration suite passing
- TestPyPI release validated (`v0.3.8-test`)
