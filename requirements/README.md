# requirements/

Since v0.6.0, provider SDKs are `pyproject.toml` pip extras (`pip install
textfsm-ai[anthropic]`). These files are a `pip install -r ...`
alternative to that syntax, for workflows that prefer requirements files
(pinned lockfiles, Docker layer caching, internal tooling built around
`-r` flags). Not part of the published package — see
`docs/getting-started/installation.md` for the full install guide.

Two sets, for two different audiences:

## `requirements-<provider>.txt`

Just `anyask[<provider>]` (which pulls in that provider's real SDK),
nothing else - mirrors the matching `pyproject.toml` extra exactly. All
LLM calls go through the [`anyask`](https://github.com/Geeks-Trident-LLC/anyask)
package rather than a vendored copy of each provider. Use this if you
already have `textfsm-ai` installed (from PyPI, or `-e .` locally) and
just want to add a provider:

```bash
pip install textfsm-ai
pip install -r requirements/requirements-anthropic.txt
```

## `dev-<provider>.txt`

One-command local dev setup: `-e .[dev]` (editable install + test/lint/
type tooling from `pyproject.toml`'s `dev` extra) plus that provider's
SDK, in a single file:

```bash
pip install -r requirements/dev-anthropic.txt
```

Deliberately *not* used for the plain-install case above - `-e .[dev]`
pulls in `pytest`/`ruff`/`black`/`mypy` and requires a local clone,
neither of which a non-dev "just add a provider" install wants. Dev
tooling versions are never duplicated into these files; they always
resolve from `pyproject.toml`'s `dev` extra, the single source of
truth, to avoid the version drift that got the old `requirements.txt`/
`requirements-dev.txt` retired in the first place.

## No `-all` variant

`pip install textfsm-ai[all]` (or `-e ".[all,dev]"` for dev) covers
"every provider SDK at once" - there's no `requirements-all.txt`/
`dev-all.txt` to keep in sync with that.
