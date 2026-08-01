# v0.6.1 — Docs & Internal Cleanup

## 📖 New: Dependency Footprint Guide
A new guide documents exactly what each `pip install
textfsm-ai[<provider>]` extra installs — package counts verified via
real clean-venv installs, plus an explanation of why some providers
(looking at you, `mistral` and `cohere`) pull in surprisingly heavy
dependency trees unrelated to making a chat-completions call.

## 📐 New: SPEC.md
A technical architecture reference now lives at the repo root,
covering how the whole system fits together — the provider registry's
lazy-loading design, the generation pipeline's correction-prompt retry
loop, the DSL engine's four-stage compile, and more.

## 🧹 Internal Cleanup
- `textfsm_ai/models/` renamed to `textfsm_ai/model_catalog/` — no
  longer collides with the "data model" meaning used elsewhere in the
  codebase (purely internal, no public-API impact)
- Removed `textfsm_ai/quota_manager.py`, unused dead code
- Consolidated `mypy.ini` into `pyproject.toml`

## 📦 Version
`0.6.0 → 0.6.1`
