# Quickstart

This guide walks through the Python API: turning a raw text sample into a
TextFSM template, then compiling that template into its AST, canonical
TextFSM, readable DSL, and recognizer patterns.

## Prerequisites

You need an API key for at least one supported provider, set as an
environment variable:

| Provider    | `provider` value | Environment variable      |
|-------------|-------------------|----------------------------|
| OpenAI      | `"openai"`        | `OPENAI_API_KEY`          |
| Anthropic   | `"anthropic"`     | `ANTHROPIC_API_KEY`       |
| Gemini      | `"gemini"`        | `GEMINI_API_KEY`          |
| DeepSeek    | `"deepseek"`      | `DEEPSEEK_API_KEY`        |
| Groq        | `"groq"`          | `GROQ_API_KEY`            |
| xAI (Grok)  | `"xai"`           | `XAI_API_KEY`             |
| Azure OpenAI| `"azure"`         | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION` |

```bash
pip install textfsm-ai
export OPENAI_API_KEY=sk-...
```

## 1. Ask an LLM to generate a template

```python
import os
import textfsm_ai

sample = """\
interface GigabitEthernet0/1
 description Uplink to core switch
interface GigabitEthernet0/2
 description Downlink to access switch
"""

result = textfsm_ai.generate(
    sample,
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-4o-mini",
)

if result.ready:
    print(result.template)     # the generated TextFSM template
    print(result.records)      # parsed records the LLM extracted
    print(result.variables)    # {"iface": "explanation of this variable", ...}
    print(result.handling)     # notes on how ambiguous lines were handled
else:
    print("Generation failed:", result.reason)
```

`generate()` never raises for an ordinary LLM/generation failure (rate
limits, retry exhaustion, an unparsable response) — check `result.ready`
and read `result.reason` instead of wrapping the call in `try`/`except`.

If you only need one piece of the result, use the matching shortcut instead
of pulling the whole object apart yourself:

```python
template = textfsm_ai.to_llm_template(sample, provider="openai", api_key=..., model="gpt-4o-mini")
records = textfsm_ai.to_llm_records(sample, provider="openai", api_key=..., model="gpt-4o-mini")
```

Note: `to_llm_template()` returns the failure reason (a string) instead of
an empty string if generation didn't succeed — it's a shortcut for the
`.template` field, not a separate cheaper call, so check `to_llm_result()`
first if you need to tell "failed" apart from "genuinely returned this
string."

## 2. Compile a template into its AST, canonical form, and recognizers

Once you have a template (from `generate()`, or one you wrote by hand),
compile it to get the parsed AST, the canonical (regex-expanded) TextFSM
template, a human-readable DSL form, and recognizer patterns:

```python
dsl = textfsm_ai.compile_dsl(result.template, result.records)

if dsl.ready:
    print(dsl.canonical)     # canonical TextFSM template
    print(dsl.readable)      # human-readable DSL
    print(dsl.recognizers)   # regex patterns that detect this block of text
    print(dsl.ast)           # the parsed TemplateAST
else:
    print("Compile failed:", dsl.reason)
```

Same shortcut pattern applies here: `to_canonical()`, `to_readable()`,
`to_recognizers()`, and `to_ast()` each take the same `(template, records)`
parameters as `compile_dsl()`.

## 3. Or run the whole pipeline in one call

`run_pipeline()` does both steps above end-to-end and packages the result
for you, in one of four verbosity modes:

```python
output = textfsm_ai.run_pipeline(
    sample,
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-4o-mini",
    mode="debug",  # "quiet" | "default" | "info" | "debug"
)

print(output.output)   # formatted text for the chosen mode
print(output.passed)   # True/False
```

## Using an Azure deployment

Azure uses a deployment name in place of `model`, plus `endpoint` and
`api_version`:

```python
result = textfsm_ai.generate(
    sample,
    provider="azure",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # deployment name
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
```

## Next steps

- See the [API Reference](../reference/index.md) for every function and
  result type.
- See the [CLI Guide](../cli/index.md) for the equivalent `textfsm-ai`
  command-line workflow.
