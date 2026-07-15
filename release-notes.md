# v0.5.1 — DSL & Pipeline CLI Commands

## ⚙️ New CLI Command: `dsl`
Compile a TextFSM template into its canonical form, readable DSL, and
recognizer patterns straight from the command line — deterministic, no LLM
call:
```bash
textfsm-ai dsl template.textfsm sample.txt
```
Same output-flag shape as `generate`: `--canonical` (default), `--readable`,
`--recognizers`, `--sections`, `--json`.

## 🚀 New CLI Command: `pipeline`
Run the full sample → LLM-generated template → DSL-compiled output flow in
one call — the CLI equivalent of the Python API's `run_pipeline()`:
```bash
textfsm-ai pipeline sample.txt --provider openai --model gpt-4o-mini --mode debug --json
```
`--mode {quiet,default,info,debug}` controls verbosity; credentials resolve
exactly like `generate`'s (same env vars, same Bedrock/Vertex AI/OCI
handling).

## 📖 Docs
Both new commands are documented in the CLI Guide; the Providers overview
page now references `pipeline` alongside `generate`.

## 🧪 Cleaner Test Output
Silenced a third-party `DeprecationWarning` from the `cohere` SDK (pinned
for Python 3.9 CI compatibility) — the full suite now runs warning-free.

## 📦 Version
`0.5.0 → 0.5.1`
