## Summary

This PR prepares the v0.6.0 release: provider SDKs are now optional
`pip install textfsm-ai[...]` extras instead of unconditional bundled
dependencies, following v0.5.2. **This is a breaking change** — see
below.

## What's Included

### Lazy Provider Loading (#57)
- `providers/registry.py` now resolves each provider's module lazily,
  only on first use, instead of eagerly importing all 19 provider
  modules (each with its own top-level SDK import) at package-import
  time.
- A missing SDK raises a clear `ImportError`: `"Provider 'bedrock'
  requires additional dependencies that are not installed. Install
  with: pip install textfsm-ai[bedrock]"`.
- Fixed a real pre-existing bug found via this work:
  `providers/__init__.py`'s `from .registry import registry` shadowed
  the `registry` submodule at the package-attribute level, silently
  breaking any dotted-attribute resolution of
  `textfsm_ai.providers.registry`.

### Provider SDKs as Pip Extras (#58)
- `pyproject.toml`'s base `dependencies` shrinks to core-only. 18
  per-provider extras added (`anthropic`, `openai` (+9 OpenAI-compatible
  aliases), `gemini`, `vertexai`, `azure`, `mistral`, `bedrock`,
  `cohere`, `oci`), plus `all` for every provider SDK at once.
- `all` is redefined from "dev + build tooling" to "every provider SDK,"
  matching the new per-provider extras convention.
- `tox.ini`'s test env now installs `dev,all` (was just `dev`) so CI
  keeps exercising every provider.
- Retired `requirements.txt`/`requirements-dev.txt` (already drifted
  from `pyproject.toml`); `docs.yml`'s docs-build job now installs the
  package directly plus the mkdocs toolchain inline.
- `docs/getting-started/installation.md`, `README.md`, `CONTRIBUTING.md`
  updated for the new install pattern.

## Breaking Changes

1. **Bare `pip install textfsm-ai` no longer installs any provider
   SDK.** Previously every provider worked out of the box; now
   `generate(provider="anthropic")` (or any provider) raises an
   `ImportError` until you `pip install textfsm-ai[anthropic]` (or
   `[all]`). Anyone with a bare install pinned in a Dockerfile/
   requirements file needs to add the relevant extra(s) on upgrade.
2. **The `all` extra changes meaning** from "dev + build tooling" to
   "every provider SDK." `pip install -e ".[all,dev]"` replaces the old
   `pip install -e ".[all]"` for a full local dev environment.

## Release Artifacts
- CHANGELOG updated for v0.6.0
- Release notes generated
- Version bumped from 0.5.2 → 0.6.0 (minor, not patch, given the
  breaking install-behavior change)

## Testing
- Full unit and integration suite passing (929 passed, 44 skipped)
- `tox -e lint` / `tox -e typecheck` clean
- Wheel built and `METADATA` inspected directly to confirm `Requires-Dist`
  is correctly scoped per extra
- Simulated a fully-blocked-SDK environment (bare install) and confirmed
  `import textfsm_ai`, the CLI, and `providers list` all still work;
  confirmed actually using a provider without its extra raises the
  correct `pip install textfsm-ai[...]` error
- TestPyPI release validated (`v0.6.0-test`)
