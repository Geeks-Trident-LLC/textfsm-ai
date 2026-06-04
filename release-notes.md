# 📝 **GitHub Release Notes**

## **v0.3.0 — Model Listing & Orchestrator Improvements**

This release introduces model listing support, provider unification, and major orchestrator enhancements.

### 🚀 New Features
- Added `list-models` command with unified model listing mixin.
- Added OpenAI‑compatible provider and updated provider registry.
- Expanded orchestrator architecture with routing, hooks, and provider interface.

### 🔧 Improvements
- Unified provider configuration schema.
- Refactored orchestrator to remove legacy config system.
- Improved CLI and provider output consistency.
- Made release pipeline idempotent and removed redundant workflow.

### 🐛 Fixes
- Corrected async handling and routing table logic.
- Fixed `$LASTEXITCODE` usage in release script.

### 🏷 Version
- Bumped version: `0.2.12 → 0.3.0`.
