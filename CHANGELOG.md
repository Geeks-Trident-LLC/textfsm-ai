
# 📘 **CHANGELOG (v0.2.0)**

## **v0.2.0 — Architecture Overhaul, APC Integration, and Language Support**

### 🚀 Features
- **Add `--lang` support** with default English output across all providers.  
  Enables consistent language control for OpenAI, Gemini, Anthropic, and DeepSeek.
- **Introduce tier-based model selection** and update config migration to support `--tier`.
- **Add `ask_ai()` public API** for programmatic access to the AI pipeline.
- **Add provider registry to `ai_router`** enabling dynamic provider loading.
- **Add provider/model configuration support** through the new config system.
- **Implement new providers**:
  - `OpenAIProvider`
  - `GeminiProvider`
  - `ClaudeProvider`
  - `DeepSeekProvider`
- **Improve CLI timing output** and correct DeepSeek provider behavior.
- **Introduce config-driven architecture** and remove legacy provider/model flags.
- **Wire CLI `generate` command to `ask_ai()`** for unified execution.

### 🔧 Refactors
- Major **config system rewrite** with strict chat-model selection and updated CLI commands.
- Improved **config init flow** and updated `UserConfig` typing.
- Provider cleanup and normalization across all backends.
- Unified config command structure and removed legacy unit tests.
- Added model listing for OpenAI, Gemini, Anthropic, and DeepSeek.

### 🧪 Tests
- Added new test suite covering:
  - router
  - API
  - CLI config commands
  - model selector
  - provider ping
  - quota manager
  - user config

### 🏷 Version
- **Bump version: `0.1.25 → 0.2.0`**
