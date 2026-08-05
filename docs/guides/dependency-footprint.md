# Dependency Footprint

`textfsm-ai` supports 18 LLM providers, but no single install needs all of
their SDKs at once. `pip install textfsm-ai` installs only the core
CLI/API — every provider SDK is an opt-in extra, either via `pip install
textfsm-ai[<provider>]` or a matching `pip install -r
requirements/requirements-<provider>.txt` file (see
[Installation](../getting-started/installation.md) for both). Every
provider SDK call is delegated to
[`anyask`](https://github.com/Geeks-Trident-LLC/anyask), a standalone
package that owns the actual provider implementations - each extra above
is a one-line pass-through to the matching `anyask[<provider>]` extra.
This page documents exactly what each extra pulls in, verified with real,
clean-venv installs — useful when you're sizing a container image or just
curious where the weight goes.

## Bare install: 6 packages

```bash
pip install textfsm-ai
```

Installs `textfsm_ai` itself plus its 5 core dependencies: `PyYAML`,
`requests`, `click`, `textfsm`, and `anyask` (`tomli` also lists as a
dependency, but only actually installs on Python <3.11). `anyask`'s own
bare install needs only `PyYAML`, already in this list, so it adds
exactly one package with zero new transitive dependencies.

This is fully functional on its own — `import textfsm_ai`, the CLI, and
`textfsm-ai providers list` all work. Only *using* a provider requires
its extra:

```pycon
>>> import textfsm_ai
>>> textfsm_ai.generate("sample", provider="anthropic", api_key="x", model="y")
ImportError: Provider 'anthropic' requires additional dependencies that
are not installed. Install with: pip install textfsm-ai[anthropic]
```

## Per-provider package counts

Each provider SDK's own dependency tree is unchanged from before -
`anyask` pins the exact same SDK versions this package used to pin
directly - so every count below is the pre-`anyask` count plus exactly
one (`anyask` itself, verified via a real `[anthropic]` install: 25
packages, vs. 24 previously).

| Extra | Total packages | What makes up the difference |
|---|---:|---|
| `[azure]` | 15 | Lightest — reuses `requests` directly, no `httpx`/`pydantic` stack |
| `[bedrock]` | 17 | `botocore` is the single largest *file* (~15MB, bundles every AWS service's API definitions), but pulls few extra packages |
| `[oci]` | 23 | Per-request cryptographic signing needs `cryptography` + `pyOpenSSL` + `PyJWT` (no bearer API key at all) |
| `[openai]` (+ 9 aliases below) | 25 | `httpx` (sync+async client) + `pydantic` (typed request/response models) |
| `[anthropic]` | 25 | Same `httpx` + `pydantic` stack as `openai`, plus `jiter`/`distro`/`docstring_parser` |
| `[gemini]` / `[vertexai]` | 32 | `httpx`+`pydantic`, **plus** `google-auth` → `cryptography` + `pyasn1` (for Application Default Credentials) |
| `[cohere]` | 32 | Unexpectedly pulls in `tokenizers` + all of `huggingface_hub` (local token counting) |
| `[mistral]` | 35 | **Heaviest** — a full OpenTelemetry SDK (`opentelemetry-api`/`-sdk`/exporters) plus `protobuf`, `googleapis-common-protos`, and `invoke` (a task-runner library) |

`[openai]` also covers `deepseek`, `groq`, `xai`, `together`, `fireworks`,
`cerebras`, `perplexity`, `openrouter`, and `moonshot` at no extra
package cost — all nine subclass the same OpenAI-compatible chat-
completions client and need nothing beyond the `openai` package itself.

**Package count and disk size are two different axes.** `oci` downloads
the single largest file (~36MB) but installs fewer total packages (23)
than `cohere` or `mistral` (32/35) — a heavy SDK author can produce
either a few large files or many small ones.

## Why some SDKs are heavier than others

The differences trace back to each provider's own upstream SDK design,
not anything this package controls:

- **HTTP client choice**: `httpx` (async-capable, used by `openai`,
  `anthropic`, `gemini`, `cohere`, `mistral`) pulls in `httpcore`, `h11`,
  `anyio`, and `sniffio` on top of itself. `azure` and `bedrock` reuse
  the plain, sync-only `requests` this package already depends on core.
- **Request/response validation**: `pydantic` (used by most of the
  `httpx`-based SDKs) brings its own compiled-Rust `pydantic_core` plus
  `annotated-types`/`typing-inspection`.
- **Credential machinery**: `gemini`/`vertexai` need `google-auth` for
  Application Default Credentials, which needs `cryptography` to verify
  signed service-account JWTs; `oci` needs `cryptography`+`pyOpenSSL`+
  `PyJWT` because it signs every request itself rather than sending a
  bearer token.
- **Unrelated SDK features**: `cohere`'s `tokenizers` dependency (for
  local token counting) and `mistral`'s OpenTelemetry stack (for
  built-in tracing) have nothing to do with making a chat-completions
  call, but ship as hard requirements of those SDKs regardless.

## How this was verified

Every number above comes from an actual `pip install` into a fresh,
empty virtual environment (not from reading `pyproject.toml` alone),
followed by `pip list`. The bare install and `[anthropic]` were both
directly re-verified after `anyask` was introduced (25 packages, up
from 24); the rest are that same pre-`anyask` count plus one, since
`anyask` pins the identical SDK versions this package used to pin
directly and adds no transitive dependencies of its own. See
[`anyask`](https://github.com/Geeks-Trident-LLC/anyask) for the
lazy-loading registry mechanism that makes per-provider opt-in possible.
