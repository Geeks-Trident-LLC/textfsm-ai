# v0.7.0 — Leaner Scope, Pip-Extras Alternative

## 📦 New: `requirements/` as a `pip install -r` Alternative
Prefer requirements files over `pip install textfsm-ai[<provider>]`?
Every provider now has a matching file:

```bash
pip install textfsm-ai
pip install -r requirements/requirements-anthropic.txt
```

Or for local dev, `requirements/dev-<provider>.txt` does an editable
install plus dev tooling plus that provider's SDK in one command.

## ⚠️ Breaking: Cost/Pricing Estimation Removed
Estimating dollar cost for an LLM call was a maintenance burden
disproportionate to what a template-generation tool should own -
maintaining an accurate price table across 18 providers, forever.
`--mode info/debug` still shows token counts and duration; it no
longer shows `estimated_cost`/`currency`/per-million pricing.

## ⚠️ Breaking: `list-models` Simplified
`list-models <provider>` now always fetches that provider's live
models directly - no more curated/`--latest`/filter modes. The
`quality`/`balance`/`speed`/`thinking` tier taxonomy is gone: deciding
which model is "best" is a model-selection-advisor concern, not
something a parsing tool should be opining on. Per-provider default
model IDs are unaffected.

## 📦 Version
`0.6.1 → 0.7.0`
