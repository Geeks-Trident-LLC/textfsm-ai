# textfsm-ai

**AI-powered TextFSM template generation, parsing assistance, and smart log extraction.**

`textfsm-ai` brings modern LLM intelligence to traditional TextFSM workflows.  
It helps you automatically generate templates, validate patterns, explain parsing logic, and accelerate network automation development.

---

## 🚀 Features

- **AI-Powered Template Generation** — Turn raw CLI output into production-ready TextFSM templates in seconds.
- **Smart Validation & Refinement** — Automatically verify template correctness and refine ambiguous patterns with AI assistance.
- **Flexible Multi-Provider AI Routing** — Use the best AI model for each task with automatic routing across supported cloud providers.

---

## 📦 Installation

```bash
pip install textfsm-ai
```

### Verify installation

```bash
textfsm-ai --version
# or
textfsm-ai version
```

Either command prints the installed version, e.g. `textfsm-ai v0.4.0`.

---

## 📚 Documentation

- **Latest docs:** https://geeks-trident-llc.github.io/textfsm-ai/latest/
- **All versions:** https://geeks-trident-llc.github.io/textfsm-ai/

---

## 🤖 What is textfsm-ai, in an LLM's view?

For an LLM, TextFSM's native syntax — regex-heavy `Value`/`Rule` definitions driving a state machine — is easy to get *almost* right and hard to get *exactly* right; small regex or state-transition mistakes are common and easy to miss. `textfsm-ai` acts as an **LLM optimizer** for TextFSM: instead of asking a model to freehand raw TextFSM syntax, it gives the model a smaller, constrained, readable DSL to generate from, then deterministically compiles that DSL into a canonical TextFSM template. The model reasons about structure and intent; `textfsm-ai` guarantees the correctness and consistency of the resulting syntax.

---

## ❓ Why do you need textfsm-ai?

- **Understands Messy Input** — Feed it raw CLI output, log lines, or any plain-text or semi-structured text; no need to hand-write parsing rules for every format and edge case.
- **No TextFSM Syntax Required** — `textfsm-ai` handles TextFSM's regex-heavy `Value`/`Rule`/state-machine syntax for you, so you don't need prior TextFSM expertise to get a working, correct template.
- **Canonical, Consistent Templates** — Every generated template goes through the same deterministic normalization step, so the same kind of input reliably produces the same shape of output every time.
- **Readable DSL** — Templates can also be expressed as a human-readable DSL that non-technical teammates can read and reason about, instead of a wall of regex.
- **Recognizer Pattern Generation** — Beyond extracting values, `textfsm-ai` can generate recognizer patterns that detect which block of text a template applies to before parsing it.
- **Real-World Applications** — Log extraction, test-data extraction and normalization, and other pipelines that turn recurring plain-text or semi-structured output into reliable, structured records.

---
