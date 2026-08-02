# v0.7.1 — Accurate Token Usage

## 🐛 Fixed: Token Usage Was Undercounted
`--mode info/debug` and `generate --usage` reported only the *last*
generation attempt's token counts, silently dropping every prior
base-prompt attempt and correction-prompt retry - each a real, billed
LLM call. A run that failed twice before succeeding on a
correction-prompt retry showed only that final call's numbers.

`Usage` now sums tokens and duration across every attempt, and gains a
`calls` field:

```
==== LLM Usage ====
LLM Calls          : 3
Input Tokens       : 412
Output Tokens      : 198
Total Tokens       : 610
LLM Duration (ms)  : 2540.0
==== END LLM Usage ====
```

`default` mode is unaffected (no usage shown there). `debug` mode's
per-stage raw pipeline breakdown was already accurate and needed no
change.

## 📦 Version
`0.7.0 → 0.7.1`
