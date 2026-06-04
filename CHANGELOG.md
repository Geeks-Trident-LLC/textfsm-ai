# 📘 **CHANGELOG (v0.3.0)**

## **v0.3.0 — Model Listing, Provider Unification, and Orchestrator Enhancements**

### 🚀 Features
- **Add `list-models` command** and introduce a shared **ModelListingMixin** across all providers.  
  Enables consistent model discovery for OpenAI, Gemini, Anthropic, DeepSeek, and future providers.
- **Add OpenAI‑compatible provider** and update provider registry/factory wiring.
- **Expand orchestrator architecture** with routing, hooks, and unified provider interface.

### 🔧 Improvements & Refactors
- **Unify `ProviderConfig` schema** and align CLI + factory logic with list‑based provider definitions.
- **Refactor orchestrator** to remove legacy config system and migrate CLI/tests to the new architecture.
- **Fix async handling, routing table, and provider outputs** across CLI and providers.
- **Make `release-prod` idempotent** and skip existing tags/releases.
- **Remove redundant release workflow** (now handled by dedicated publish pipelines).

### 🐛 Fixes
- Correct PowerShell conditional to use `$LASTEXITCODE`.

### 🏷 Version
- **Bump version: `0.2.12 → 0.3.0`**
