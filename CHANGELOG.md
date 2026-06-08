## [0.3.2] - 2026-06-07

### Refactor
- Rewrote LLM model classification system (OpenAI, Gemini, Anthropic, DeepSeek)
- Added new `patterns.py` with updated regex for Claude 4.x, Gemini 2.5/3.x, GPT‑4o/5.x, DeepSeek v4/R1
- Introduced new curated model registry under `textfsm_ai/models/curated-models.yaml`
- Removed outdated `providers/curated-models.yaml`
- Unified provider API across OpenAI, Gemini, Anthropic, Azure, DeepSeek
- Updated provider implementations to use consistent config mapping (`temperature`, `max_tokens`, etc.)
- Fixed Gemini provider to use correct `config=` parameter
- Improved model listing logic via updated `model_listing_mixin.py`
- Updated CLI commands (`generate`, `list-models`, `providers`, `orchestrator`) to use new model registry

### Improvements
- Better error normalization across providers
- More consistent model naming and tier grouping
- Updated curated model lists for all providers
- Improved routing logic in orchestrator

### Tests
- Added new unit tests for classifier, patterns, curated models
- Updated provider tests to reflect new API and naming
- Synced tests with new provider behavior

### Fixes
- Improved release-prod tag handling logic

### Breaking Changes
- Removed old curated-models file under `providers/`
- Provider interfaces updated; older configs may require adjustments
