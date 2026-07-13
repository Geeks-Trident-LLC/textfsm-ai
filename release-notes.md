# v0.4.2 — Public API Facade, New Docs, ~99% Test Coverage

## 🐍 Standardized Public Python API
`textfsm_ai` now has a small, consistent top-level API instead of requiring
callers to know the internal package layout:

- `generate()` / `compile_dsl()` / `run_pipeline()` — always return a full
  result object (`LLMResult`, `DSLResult`, `DeliveryOutput`), never raise for
  expected failures (rate limits, retry exhaustion, invalid templates);
  check `.ready`/`.reason` instead
- `to_llm_result` / `to_llm_template` / `to_llm_records` / `to_llm_variables` /
  `to_llm_handling` and `to_dsl_result` / `to_ast` / `to_canonical` /
  `to_readable` / `to_recognizers` — shortcuts with identical parameters,
  for when you only need one piece of the result
- `LLMResult`, `DSLResult`, `TemplateAST`, `DeliveryOutput`, and
  `ValidationResult` all importable directly from `textfsm_ai`
- Removed `ask_ai()`, the old raw single-provider-call primitive, superseded
  by `generate()`/`run_pipeline()`

## 📚 New Documentation
- **Quickstart** — the full API, function by function, with runnable examples
- **API Reference** — auto-generated from docstrings, every public
  function/type
- **CLI Guide** — every command, verified against the live CLI
- **Human-in-the-Loop Review** — a new guide for reviewing a generated
  template without reading or writing regex: interpret the plain-English
  "readable" DSL form, then verify it against reality by actually running
  the template and diffing the result against both the LLM's own claim and
  your own expectation
- Removed broken/stale doc pages, including one describing a golden-test
  framework that was never actually built

## 🐛 Bug Fix
Fixed `generate()` sourcing its `.ready`/`.reason` status from the wrong
place — it now reflects the authoritative pipeline-level outcome (retries,
template-syntax validation included) rather than a shallower internal
signal that could report success for a pipeline that had actually failed.

## 🧪 Test Coverage
Raised to ~99% across nearly the entire codebase — every file with a
genuinely testable gap is now closed, with the remaining handful of missed
lines confirmed as structurally unreachable dead code (unknown-enum-value
guards, abstract-method stubs).

## 📦 Version
`0.4.1 → 0.4.2`
