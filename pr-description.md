
# 📦 **Pull Request Description**

## **feat: APC integration, language support, new config system, and provider upgrades**

This PR delivers a major architectural upgrade to `textfsm-ai`, introducing a unified APC layer, a new configuration system, language control, and expanded provider support.

### **Key Highlights**

#### **1. Language Support**
- Added `--lang` flag to CLI (`generate` command).
- Default output language is now English.
- DeepSeek provider updated with language-aware system prompts.

#### **2. APC Integration**
- Introduced `ask_ai()` as the unified public API.
- Wired CLI `generate` command to APC pipeline.
- Added provider registry and model configuration support.

#### **3. New Config System**
- Tier-based model selection.
- Updated `config init`, `config migrate`, and `config show`.
- Strong typing for `UserConfig`.

#### **4. Provider Enhancements**
- Implemented OpenAI, Gemini, Claude, and DeepSeek providers.
- Added model listing for all providers.
- Normalized provider interfaces.

#### **5. CLI Improvements**
- Improved timing output.
- Removed legacy provider/model flags.
- Unified config command structure.

#### **6. Test Suite Expansion**
- Added tests for router, API, CLI, config, providers, quota, and model selector.

### **Version**
- Bumped version to `v0.2.0`.

This PR completes the APC feature branch and prepares the project for orchestrator integration in the next phase.
