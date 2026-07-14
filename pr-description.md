## Summary

This PR prepares the v0.5.0 release: a new Oracle OCI provider, a
breaking standardization of every provider's environment variable naming,
a new providers overview doc page, a refreshed docs homepage, and a ~4x
test suite speedup, following v0.4.2.

## What's Included

### New Provider
- Oracle Cloud Infrastructure (OCI) Generative AI (`provider="oci"`) —
  Meta Llama and xAI Grok models via OCI's Generic chat format
- Authenticates via `~/.oci/config` (no project-level API key, same shape
  as Bedrock/Vertex AI); new `compartment_id` parameter / `--compartment-id`
  CLI flag threaded through the full plumbing chain
- Deliberately excluded from auto-routing — its `meta.`/`xai.` model-ID
  prefixes collide with Bedrock's re-hosted namespace, so `--provider oci`
  must be explicit

### Breaking Change: Environment Variable Standardization
- Every provider's env vars now follow one uniform `<PROVIDER>_<FIELD>`
  pattern, no exceptions:
  - `AZURE_OPENAI_API_KEY`/`AZURE_OPENAI_ENDPOINT`/`AZURE_OPENAI_API_VERSION`/
    `AZURE_OPENAI_DEPLOYMENT` → `AZURE_API_KEY`/`AZURE_ENDPOINT`/
    `AZURE_API_VERSION`/`AZURE_DEPLOYMENT`
  - `AWS_REGION`/`AWS_DEFAULT_REGION` → `BEDROCK_REGION`/`BEDROCK_DEFAULT_REGION`
  - `GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION` → `VERTEXAI_PROJECT`/`VERTEXAI_REGION`
- None of the renamed vars were read by the underlying SDKs themselves
  (boto3/google-genai/azure-ai-inference always get explicit values passed
  in), only by this app's own `os.getenv()` calls — no functional reason to
  keep the old ecosystem-convention names once Azure/AWS/GCP naming is
  already being broken from for consistency
- **Anyone with the old env var names already set must update them.**

### Documentation
- New `docs/providers/index.md` — single overview page listing all 18
  providers, credentials, extra params, Shape A/B split, and
  routing-collision notes
- Refreshed `docs/index.md` — intro now leads with the AI-powered
  generation angle (the actual headline feature) instead of reading like a
  generic parsing library; removed the false "Zero external dependencies"
  claim; replaced Documentation/Installation sections with a single
  "Explore the Docs" links section

### Test Suite
- Removed `tests/unit/test_providers.py` and
  `tests/unit/test_providers_openai_compat.py` — fully redundant with
  `tests/unit/providers/*.py`, zero coverage loss
- Added session-scoped SSL-context caching (`tests/unit/conftest.py`) —
  provider/orchestrator-factory tests were spending most of their runtime
  re-parsing the CA certificate bundle on every real SDK client
  construction; full suite runtime drops from 60+s to ~15-20s
- Added a test covering `Orchestrator.run()`'s previously-untested
  retry-exhaustion re-raise path — `orchestrator.py` moves from 91% to
  100% coverage

## Release Artifacts
- CHANGELOG updated for v0.5.0
- Release notes generated
- Version bumped from 0.4.2 → 0.5.0

## Testing
- Full unit and integration suite passing (901 passed, 44 skipped)
- `tox -e format,lint,typecheck` clean
- TestPyPI release validated (`v0.5.0-test`)
