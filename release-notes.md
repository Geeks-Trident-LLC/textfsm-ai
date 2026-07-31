# v0.5.2 — Smarter Template Validation & Consistent Date/Time Naming

## 🔍 Looser Pattern Boundaries, Automatically Suggested
The template validator now catches an overly-strict pattern shape: a rule
ending in `\s+` (or starting with `^\s+`) requires at least one whitespace
character to actually be present in the line, silently rejecting samples
where it's absent. `find_template_issues()` now flags this and suggests
`\s*` instead — feeding straight into the existing LLM correction loop.

## 🕐 Consistent Date/Time Variable Names
Generated templates now follow one naming convention for date/time
fields instead of inventing synonyms run to run:
- Whole date+time in one field → `datetime`
- Date only → `date`, time only → `time`
- Split into parts → `weekday`, `month`, `day`, `year`, `hour`, `minute`,
  `second`, `am_pm`, `timezone`

`timezone` covers any representation your sample throws at it — `PDT`,
`UTC`, `+08:00`, `Z`, and so on all map to the same field name.

## 📦 Version
`0.5.1 → 0.5.2`
