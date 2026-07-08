# v0.4.0 — Template Delivery, Unified Generation, Pricing Engine

## 🚀 New Delivery Pipeline
A fully unified template‑delivery subsystem now powers all DSL → AST → render →
package assembly flows. This replaces the legacy delivery modules and provides:

- Canonicalized pattern rendering
- Recognizer and readable renderers
- Strict typing across DSL, generation, and orchestrator layers
- Updated AST parser with nested pattern/action rules

## 🧠 Unified Generation Architecture
The old generation engines have been removed and replaced with the new
GenerationController, featuring:

- Structured retry logic with retryable/unretryable error gating
- Provider‑aware generation pipeline
- Updated provider registry and CLI integration

## 💵 New Pricing Engine
A complete pricing subsystem is now available:

- OpenAI, Azure, Anthropic, DeepSeek, Gemini pricing tables
- Longest‑prefix model family resolution
- Reasoning‑token billing
- Sonnet‑5 intro‑pricing auto‑update
- Full pytest suite

## 🛠 Provider Improvements
- Azure provider endpoint fixes and unified model mapping
- Updated providers.yaml defaults
- Expanded CLI provider commands and tests

## 🧪 Testing
- New pricing tests
- Updated CLI tests for all providers
- Updated integration tests for generation and delivery

## 📦 Version
`0.3.8 → 0.4.0`
