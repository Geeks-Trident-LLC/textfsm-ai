# v0.6.0 — Provider SDKs Are Now Optional

## 📦 Slimmer Installs
`pip install textfsm-ai` now installs only the core CLI/API — no LLM
provider SDK bundled in. Add the provider(s) you actually use:

```bash
pip install textfsm-ai[anthropic]
pip install textfsm-ai[openai]      # also covers deepseek/groq/xai/
                                     # together/fireworks/cerebras/
                                     # perplexity/openrouter/moonshot
pip install textfsm-ai[all]         # every provider SDK
```

The heaviest SDK, Oracle's `oci` (~36MB plus transitive crypto libs), is
now fully opt-in instead of installed unconditionally — a meaningful
win for container images that only ever call one or two providers.

Skip a provider's extra and try to use it anyway? You get a clear error
telling you exactly which extra to install, instead of a confusing
import failure buried deep in an unrelated stack trace.

## ⚠️ Breaking Changes
- Bare `pip install textfsm-ai` no longer works for any provider out of
  the box — add the extra(s) you need, or `[all]` for the old
  bundle-everything behavior.
- The `all` extra now means "every provider SDK," not "dev + build
  tooling." Local development is now `pip install -e ".[all,dev]"`.

## 📦 Version
`0.5.2 → 0.6.0`
