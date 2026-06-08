## 🚀 v0.3.2 — LLM Extraction & Generation Refactor

This release introduces a major refactor of the model classification system, curated model registry, and provider integrations.

### ✨ Highlights
- New unified model classifier (OpenAI, Gemini, Anthropic, DeepSeek)
- Updated regex patterns for Claude 4.x, Gemini 2.5/3.x, GPT‑4o/5.x
- New curated model registry under `textfsm_ai/models/curated-models.yaml`
- Unified provider API with consistent config mapping
- Improved CLI commands for model listing and generation
- Fixed Gemini provider (`config=` instead of deprecated `generation_config`)

### 🔧 Improvements
- Better error handling across providers
- Cleaner model normalization
- Updated curated model lists for all providers
- Improved orchestrator routing logic

### 🧪 Tests
- Added new tests for classifier, patterns, curated models
- Updated provider tests to reflect new API

### 🛠 Fixes
- Improved release-prod tag handling logic

### 🛠 Breaking Changes
- Removed old curated-models file under `providers/`
- Provider interfaces updated; older configs may need adjustments

### 📦 Release Status
This version has passed **release-test** and is ready for **release-prod**.
