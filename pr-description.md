# 📦 **Pull Request Description**

## **feat: model listing, provider unification, and orchestrator upgrades**

This PR delivers a set of improvements across providers, orchestrator, and release automation.

### **Key Additions**
- Introduced `list-models` CLI command.
- Added `ModelListingMixin` to unify model discovery across all providers.
- Added OpenAI‑compatible provider and updated provider registry/factory wiring.

### **Refactors**
- Unified `ProviderConfig` schema and aligned CLI/factory with list‑based provider definitions.
- Removed legacy config system and migrated CLI/tests to the new orchestrator architecture.
- Improved orchestrator routing, hooks, and provider interface consistency.

### **Fixes**
- Corrected async handling, routing table, and provider outputs.
- Fixed PowerShell `$LASTEXITCODE` usage in release script.

### **Release Pipeline**
- Removed redundant `release.yml` workflow.
- Ensured publish pipelines cleanly separate TestPyPI and PyPI releases.
- Made `release-prod` idempotent and safe to rerun.

### **Version**
- Bumped version to `v0.3.0`.

This PR prepares the project for upcoming orchestrator features and multi‑provider enhancements.