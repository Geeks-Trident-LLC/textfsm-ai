## Summary

This PR prepares the v0.7.1 patch release: a fix for undercounted
token usage in `--mode info/debug` and `generate --usage`, following
v0.7.0. No breaking changes.

## What's Included

### Fix: Accumulate Token Usage Across All Retries (#68)
- `Usage` previously reported only the **last** generation stage's
  token counts, silently dropping every prior base-prompt attempt and
  correction-prompt retry - each of which is a real, billed LLM call.
  A run that failed twice before succeeding on the third attempt
  showed only the third attempt's usage.
- `Usage` gains a `calls` field (count of LLM calls actually made) and
  now sums `input_tokens`/`output_tokens`/`total_tokens`/
  `llm_duration_ms` across every stage in `GenerationPipeline.stages`.
- `generate --usage` had the identical last-stage-only bug in a
  separate code path; fixed with the same new `accumulate_usage()`
  helper (`delivery/assembly/builder.py`) to avoid duplicating the
  summation logic.
- `default` mode is unaffected (no usage shown there); `info`/`debug`
  both show the same accumulated summary - `debug`'s per-stage raw
  breakdown via the dumped pipeline JSON was already accurate and is
  unchanged.

## Release Artifacts
- CHANGELOG updated for v0.7.1
- Release notes generated
- Version bumped from 0.7.0 → 0.7.1 (patch - bug fix, no breaking
  changes)

## Testing
- Full unit and integration suite passing (829 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- `mkdocs build --strict` clean
- New tests covering multi-stage accumulation in both the delivery
  builder and the `generate` CLI command
- TestPyPI release validated (`v0.7.1-test`)
