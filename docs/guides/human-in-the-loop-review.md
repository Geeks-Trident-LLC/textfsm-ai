# Human-in-the-Loop Review

The LLM will hand you back a template, some parsed records, and its own
notes about how it interpreted your sample. That's a good first draft — but
before you trust it in production, someone should sanity-check it. This
guide walks through a review process that **does not require reading or
writing regex**: you read the plain-English "readable DSL" form instead,
then let the tool itself prove whether the template actually behaves the
way the LLM claims.

No coding background is assumed beyond "can read a Python snippet and run
it." If you can follow a recipe, you can follow this.

## The workflow at a glance

1. **Prepare** — a text sample, and API credentials for one LLM provider.
2. **Extract** — ask the LLM for a template, records, variable
   explanations, and handling notes.
3. **Build the DSL** — compile that template into three views: a
   canonical (machine) form, a readable (human) form, and recognizer
   patterns.
4. **Review** — read the readable form to judge whether the logic looks
   right, then run the canonical form for real and compare its output
   against both the LLM's own records and your own expectations.

## 1. Prepare your inputs

You need the sample text you want parsed, plus credentials for one
supported provider (see the [Quickstart](../getting-started/quickstart.md#prerequisites)
for the full provider/environment-variable table).

```python
import os
import textfsm_ai

sample = """\
interface GigabitEthernet0/1
 description Uplink to core switch
"""

provider = "openai"
api_key = os.environ["OPENAI_API_KEY"]
model = "gpt-4o-mini"
```

## 2. Extract: ask the LLM

```python
llm = textfsm_ai.generate(sample, provider=provider, api_key=api_key, model=model)

if not llm.ready:
    raise SystemExit(f"Generation failed: {llm.reason}")

print(llm.template)     # the LLM-authored template
print(llm.records)      # records the LLM claims it parsed from the sample
print(llm.variables)    # {"iface": "the interface name", "desc": "the port description"}
print(llm.handling)     # notes on anything ambiguous the LLM had to decide about
```

At this point you have the LLM's own account of what it did — but it's
just a claim. The rest of this guide is about checking that claim.

## 3. Build the DSL

Compile the LLM's template into three views, all derived from the same
underlying structure:

```python
dsl = textfsm_ai.compile_dsl(llm.template, llm.records)

if not dsl.ready:
    raise SystemExit(f"Compiling failed: {dsl.reason}")

print(dsl.canonical)     # the machine-form TextFSM template (regex-heavy)
print(dsl.readable)      # the same logic, in plain-English-ish form
print(dsl.recognizers)   # regex patterns — set aside for step 5
```

For the sample above, `dsl.readable` looks like this:

```text
state Start:
  start() interface mixed-word(var-iface, options-Required) -> Continue
  start() description word-group(var-desc) -> Record
```

You never need to look at `dsl.canonical`'s regex directly — `dsl.readable`
is the review surface.

## 4. Review: read the readable DSL

Each line reads left to right as a rule: *if the start of the line matches
this shape, do this action.* You don't need to know regex to follow it —
just this small cheat sheet:

| You see | It means |
|---|---|
| `start()` | "beginning of the line" |
| a bare word, e.g. `interface` | that literal word must appear here |
| `word(var-x)`, `mixed-word(var-x)`, `digit(var-x)`, `word-group(var-x)`, ... | capture this piece of text into a field named `x` |
| `options-Required` | this field must be present, or the line doesn't match |
| `-> Continue` | keep reading more lines before finishing this record |
| `-> Record` | save everything captured so far as one output row, then start the next record |

Reading the example above in plain English:

> "If a line starts with the word `interface` followed by some
> alphanumeric text, save that text as `iface` (it's required), and keep
> reading. If a later line starts with `description` followed by one or
> more words, save that as `desc`, then save the record."

That's the same question a non-technical reviewer needs to answer either
way: *does this match what I actually meant by my sample?* Now they can
answer it without opening a regex reference.

If something looks wrong here — a field capturing the wrong shape of text,
a missing `Required`, an action that fires too early or too late — you've
caught it without running anything, and can go back to step 2 with a
clearer sample or ask the LLM to try again.

## 5. Verify: run the canonical template for real

Reading the readable DSL tells you whether the *logic* looks reasonable.
It doesn't prove the canonical template actually produces the records the
LLM said it would — for that, run it:

```python
parsed = textfsm_ai.parse_to_dicts(dsl.canonical, sample)
```

`parsed` is the *ground truth*: real output from really running the
compiled template against your sample, independent of anything the LLM
told you. Now there are three things to compare:

- **`llm.records`** — what the LLM *claimed* it parsed
- **`parsed`** — what the canonical template *actually* produces
- **your own expectation** — what you, the human, believe the sample should yield

```python
import difflib
import json


def show_diff(label_a, records_a, label_b, records_b):
    a = json.dumps(records_a, indent=2, sort_keys=True).splitlines()
    b = json.dumps(records_b, indent=2, sort_keys=True).splitlines()
    diff = list(difflib.unified_diff(a, b, fromfile=label_a, tofile=label_b, lineterm=""))
    print("\n".join(diff) if diff else f"{label_a} and {label_b} match.")


expected = [{"iface": "GigabitEthernet0/1", "desc": "Uplink to core switch"}]

show_diff("llm.records", llm.records, "parsed (canonical)", parsed)
show_diff("parsed (canonical)", parsed, "expected", expected)
```

How to read the outcome:

- **`llm.records` matches `parsed`** — the LLM's self-report is trustworthy;
  the template genuinely does what the LLM said it does.
- **They *don't* match** — the LLM's description of its own template was
  wrong. Trust `parsed`, not `llm.records` — it came from actually running
  the compiled template.
- **`parsed` doesn't match your own `expected`** — the template's *logic*
  is wrong, not just the self-report. This is the case that needs a human:
  go back to step 2 with a clearer or more representative sample, or edit
  the template by hand.

## 6. Recognizers: set aside for later

`dsl.recognizers` isn't part of this review loop. It's a set of regex
patterns for a different job entirely: letting some *other* tool or
pipeline detect which template applies to a given block of text, before
parsing it — useful once you have a library of templates and need to route
incoming text to the right one automatically. Keep it on hand, but there's
nothing to review here today.

## Next steps

- [Quickstart](../getting-started/quickstart.md) — the full function-by-function walkthrough.
- [API Reference](../reference/index.md) — every function and result type.
