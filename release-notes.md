# v0.4.1 — Package Refactor, CI Fix, ~95% Test Coverage

## 🧹 DSL Package Refactor
`dsl/core/nodes.py`, the largest module in the codebase, has been split into a
proper package (`dsl/core/nodes/`) organized by responsibility:

- `groups.py` — keyword group constants and lookup
- `base.py` — `BaseNode`
- `leaf.py` — literal and keyword node types
- `modifiers.py` — optional/maybe/not node types
- `quantifiers.py` — zero‑or‑more, one‑or‑more, exact, and range node types
- `factory.py` — `create_node()`

All existing import paths continue to work unchanged.

## 🛠 CLI & Packaging Fixes
- Added a `--version` CLI flag
- Removed a stray `pytest.ini` that was silently shadowing the project's real
  pytest configuration in `pyproject.toml` (including coverage options)
- Fixed Makefile recipe tabs and aligned `pre-commit` hooks with pinned tox
  lint/format/typecheck versions
- CI now also triggers on pushes to `develop`, not just `main`

## 🐛 Bug Fixes
- Fixed an unreachable error branch in `orchestrator/factory.py` for unknown
  provider types — now correctly raises `ValueError`
- Fixed `generate_cmd.py` referencing a nonexistent `pconf.api_key` attribute
  and mapping Gemini's API key to the wrong environment variable

## 🧪 Test Coverage
Overall test coverage raised to ~95%, with dedicated new test suites added for:

- All provider modules (OpenAI, Azure, Anthropic, DeepSeek, Gemini, OpenAI‑compatible)
- Delivery assembly, controller, and engine modules
- `dsl/core/nodes/factory.py`
- `generation/support/llm_extractor.py` and `dsl/engine/dsl_engine.py`
- `core/serializable.py`, `core/dotdict.py`, `core/utils/template.py`
- Remaining CLI and packaging gaps

## 📦 Version
`0.4.0 → 0.4.1`
