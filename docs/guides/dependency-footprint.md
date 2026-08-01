# Dependency Footprint

`textfsm-ai` supports 18 LLM providers, but no single install needs all of
their SDKs at once. Since [v0.6.0](../changelog.md), `pip install
textfsm-ai` installs only the core CLI/API — every provider SDK is an
opt-in extra (see [Installation](../getting-started/installation.md)).
This page documents exactly what each extra pulls in, verified with real,
clean-venv installs — useful when you're sizing a container image or just
curious where the weight goes.

## Bare install: 5 packages

```bash
pip install textfsm-ai
```

Installs only `textfsm_ai` itself plus its 4 core dependencies:
`PyYAML`, `requests`, `click`, `textfsm` (`tomli` also lists as a
dependency, but only actually installs on Python <3.11).

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

| Extra | Total packages | What makes up the difference |
|---|---:|---|
| `[azure]` | 14 | Lightest — reuses `requests` directly, no `httpx`/`pydantic` stack |
| `[bedrock]` | 16 | `botocore` is the single largest *file* (~15MB, bundles every AWS service's API definitions), but pulls few extra packages |
| `[oci]` | 22 | Per-request cryptographic signing needs `cryptography` + `pyOpenSSL` + `PyJWT` (no bearer API key at all) |
| `[openai]` (+ 9 aliases below) | 24 | `httpx` (sync+async client) + `pydantic` (typed request/response models) |
| `[anthropic]` | 24 | Same `httpx` + `pydantic` stack as `openai`, plus `jiter`/`distro`/`docstring_parser` |
| `[gemini]` / `[vertexai]` | 31 | `httpx`+`pydantic`, **plus** `google-auth` → `cryptography` + `pyasn1` (for Application Default Credentials) |
| `[cohere]` | 31 | Unexpectedly pulls in `tokenizers` + all of `huggingface_hub` (local token counting) |
| `[mistral]` | 34 | **Heaviest** — a full OpenTelemetry SDK (`opentelemetry-api`/`-sdk`/exporters) plus `protobuf`, `googleapis-common-protos`, and `invoke` (a task-runner library) |

`[openai]` also covers `deepseek`, `groq`, `xai`, `together`, `fireworks`,
`cerebras`, `perplexity`, `openrouter`, and `moonshot` at no extra
package cost — all nine subclass the same OpenAI-compatible chat-
completions client and need nothing beyond the `openai` package itself.

**Package count and disk size are two different axes.** `oci` downloads
the single largest file (~36MB) but installs fewer total packages (22)
than `cohere` or `mistral` (31/34) — a heavy SDK author can produce
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
followed by `pip list` and a functional check that the installed
provider resolves via `get_provider_by_name()` while every
*other* provider correctly raises the `pip install textfsm-ai[...]`
error. See `textfsm_ai/providers/registry.py` for the lazy-loading
mechanism that makes this possible.
