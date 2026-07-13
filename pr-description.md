## Summary

This PR prepares the v0.4.2 release: a new standardized public Python API,
the documentation to go with it, and a further pass of test coverage
across the codebase, following v0.4.1.

## What's Included

### Public API
- New facade: `generate()`/`compile_dsl()`/`run_pipeline()` (verb functions,
  always return a full result object, never raise for expected failures)
  plus `to_llm_result`/`to_llm_template`/`to_llm_records`/`to_llm_variables`/
  `to_llm_handling` and `to_dsl_result`/`to_ast`/`to_canonical`/`to_readable`/
  `to_recognizers` shortcuts with identical parameters to their verb function
- New `LLMResult`/`DSLResult` result types (`textfsm_ai/api_models.py`);
  `TemplateAST`, `DeliveryOutput`, `ValidationResult` now also exported at
  the top level
- Removed `ask_ai()`, superseded by `generate()`/`run_pipeline()`

### Documentation
- Quickstart guide covering the full API end to end
- mkdocstrings-generated API Reference (all public functions/types)
- Real CLI Guide (every command, verified against the live CLI)
- New Human-in-the-Loop Review guide: reviewing a generated template using
  the plain-English "readable" DSL form and a real parse-and-diff step,
  with no regex required
- Removed broken/stale docs pages and a nonexistent golden-test framework doc

### Bug Fix
- `generate()` now sources `.ready`/`.reason` from the top-level generation
  pipeline (accounts for retries and template-syntax validation) instead of
  the nested LLM response object — the old logic could report success for a
  pipeline that had actually failed

### Test Coverage
- Raised to ~99% across nearly the entire codebase, closing every file that
  had a genuinely testable gap

## Release Artifacts
- CHANGELOG updated for v0.4.2
- Release notes generated
- Version bumped from 0.4.1 → 0.4.2

## Testing
- Full unit and integration suite passing
- `tox -e format,lint,typecheck` clean
- TestPyPI release validated (`v0.4.2-test`)
