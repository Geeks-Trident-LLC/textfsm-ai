## Summary

This PR introduces a major refactor of the LLM extraction and generation pipeline.  
It modernizes model classification, updates provider integrations, and replaces the curated model system with a unified registry.

## Key Changes

### 🔧 Model Classification
- New `classifier.py` with tier-based grouping (quality, balance, speed, thinking)
- New `patterns.py` supporting:
  - Claude 4.x (opus/sonnet/haiku)
  - Gemini 2.5 / 3.x (pro/flash/flash-lite)
  - OpenAI GPT‑4o / GPT‑5.x families
  - DeepSeek v4 + R1 + Reasoner

### 📦 Curated Models
- Added new curated model registry under `textfsm_ai/models/curated-models.yaml`
- Removed outdated `providers/curated-models.yaml`
- Updated CLI model listing to use the new registry

### 🤖 Provider Refactor
- Unified provider API across OpenAI, Gemini, Anthropic, Azure, DeepSeek
- Fixed Gemini provider to use `config=` instead of deprecated `generation_config`
- Normalized temperature/max_tokens mapping across providers
- Improved error handling and normalization

### 🧰 CLI Improvements
- Updated `generate`, `list-models`, `providers`, and `orchestrator` commands
- Added provider-aware model resolution
- Improved output formatting and error messages

### 🧪 Tests
- Added new tests for classifier, patterns, curated models
- Updated provider tests to reflect new API
- Synced tests with new provider behavior

### 🛠 Fixes
- Improved release-prod tag handling logic

## Breaking Changes
- Removed old curated-models file under `providers/`
- Provider interfaces updated; older configs may require adjustments

## Motivation
This refactor prepares the codebase for:
- consistent provider behavior  
- future model additions  
- improved reliability  
- better CLI ergonomics  

## Release Plan
- `release-test` completed successfully  
- After merge to `main`, run `release-prod` to publish v0.3.2  
