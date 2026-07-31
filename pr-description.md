## Summary

This PR prepares the v0.5.2 release: a new template-validator check for
overly-strict `\s+` pattern boundaries, and a consistent date/time
variable-naming rule added to the LLM generation prompt, following v0.5.1.

## What's Included

### Validator: Pattern Boundary Whitespace
- New `check_pattern_boundary_whitespace()`, wired into
  `find_template_issues()`
- A rule pattern ending in `\s+` (or `\s+$$`) is flagged as
  `pattern_trailing_whitespace_plus`, suggesting `\s*` (or `\s*$$`)
- A rule pattern starting with `^\s+` is flagged as
  `pattern_leading_whitespace_plus`, suggesting `^\s*`
- `\s+` at a boundary requires at least one whitespace character to be
  present in the sample line; `\s*` matches just as well when it's there,
  without rejecting lines where it's absent
- Findings flow through the existing correction-prompt loop
  (`prompts.yaml`'s `{finding}` placeholder) like every other check

### Prompt: Consistent Date/Time Variable Names
- New rule in `prompts.yaml`'s `Value Rules` section:
  - Whole date+time as one field -> `datetime`
  - Date only, one field -> `date`
  - Time only, one field -> `time`
  - Separate fields -> `weekday`, `month`, `day`, `year`, `hour`, `minute`,
    `second`, `am_pm`, `timezone`
- `timezone` explicitly covers any representation (`PDT`, `PST`, `UTC`,
  `GMT`, `+08:00`, `-05:00`, `Z`, etc.)
- Separate-fields granularity deliberately includes `hour`/`minute`/
  `second` individually — the idiomatic TextFSM pattern for
  colon-separated timestamps
- Reaches both the initial generation prompt and every correction-retry
  prompt, since `correction_prompt()` builds itself from `{base}`

## Release Artifacts
- CHANGELOG updated for v0.5.2
- Release notes generated
- Version bumped from 0.5.1 → 0.5.2

## Testing
- Full unit and integration suite passing (922 passed, 44 skipped)
- `tox -e lint` clean
- TestPyPI release validated (`v0.5.2-test`)
