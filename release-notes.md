
# 📝 **GitHub Release Notes**

## **v0.2.0 — APC Integration, Language Support, and New Config System**

This release introduces a major architectural upgrade to `textfsm-ai`, including a new APC layer, improved provider support, and a fully redesigned configuration system.

### 🚀 New Features
- Added `--lang` flag with default English output.
- Introduced `ask_ai()` public API.
- Added provider registry and model configuration support.
- Implemented OpenAI, Gemini, Claude, and DeepSeek providers.
- Added tier-based model selection.
- Improved CLI timing output.

### 🔧 Improvements & Refactors
- Complete rewrite of config system.
- Unified CLI config commands.
- Provider cleanup and normalization.
- Added model listing for all providers.

### 🧪 Testing
- Added comprehensive test suite for router, API, CLI, config, providers, quota, and model selector.

### 🏷 Version
- Bumped version: `0.1.25 → 0.2.0`.

---

## **v0.2.0-test — Test Release**

This is the TestPyPI release for validation of packaging, provider integration, and CLI behavior.

Contains the same changes as `v0.2.0`, published for testing purposes only.
