# v0.8.0 — Provider Calls Delegated to `anyask`

## 🔧 Changed: Providers Now Powered by `anyask`
All 18 LLM provider implementations are now delegated to
[`anyask`](https://github.com/Geeks-Trident-LLC/anyask) - a standalone
package (same maintainer) that owns the actual per-provider SDK calls -
instead of being vendored inside `textfsm-ai`.

**Nothing changes for normal usage.** `pip install
textfsm-ai[anthropic]` (or any other provider) still works exactly as
before; it now pulls in `anyask[anthropic]` instead of the SDK
directly, adding exactly one extra package with zero new transitive
dependencies.

## ⚠️ Breaking (Internal Only): `orchestrator/` Removed
`textfsm_ai.orchestrator` and the `textfsm-ai orchestrator route/run`
CLI commands are gone. This was an auto-routing/fallback layer that
turned out to be unused by the real `generate`/`pipeline` path (which
always takes an explicit `--provider`) - dead weight duplicating
`generate`. `providers test` (a quick connectivity check) is kept, now
with a required `--provider` flag instead of guessing the provider
from the model name.

## ⚠️ Breaking (Internal Only): Module Removals
`textfsm_ai.providers.<x>_provider` modules and `OrchestratorConfig`
(renamed `ProvidersConfig`) are gone. Neither was part of the
documented public API - only relevant if you were importing internals
directly.

## 📦 Version
`0.7.1 → 0.8.0`
