# Installation

`textfsm-ai` supports Python 3.9+ and works on all major platforms.

## Install from PyPI

```bash
pip install textfsm-ai
```

This installs the core CLI/API only - no LLM provider SDK. Pick the
provider(s) you actually use as an extra:

```bash
pip install textfsm-ai[openai]        # OpenAI (also covers deepseek, groq,
                                       # xai, together, fireworks, cerebras,
                                       # perplexity, openrouter, moonshot -
                                       # all OpenAI-compatible, no extra
                                       # SDK needed beyond openai)
pip install textfsm-ai[anthropic]     # Anthropic Claude
pip install textfsm-ai[gemini]        # Google Gemini
pip install textfsm-ai[vertexai]      # Google Vertex AI
pip install textfsm-ai[azure]         # Azure AI Inference / Azure OpenAI
pip install textfsm-ai[mistral]       # Mistral AI
pip install textfsm-ai[bedrock]       # Amazon Bedrock
pip install textfsm-ai[cohere]        # Cohere
pip install textfsm-ai[oci]           # Oracle Cloud Infrastructure
```

Need more than one? Combine extras: `pip install textfsm-ai[anthropic,gemini]`.

Or install every provider SDK at once:

```bash
pip install textfsm-ai[all]
```

Provider SDK imports are lazy - if you skip a provider's extra and try to
use it anyway, you get a clear error telling you which extra to install,
rather than a confusing import failure.

See the [Dependency Footprint](../guides/dependency-footprint.md) guide
for exactly how many packages each extra installs.

### Alternative: `pip install -r requirements/...`

Prefer requirements files over the `pkg[extra]` syntax (pinned lockfiles,
Docker layer caching, internal tooling that expects a `-r` flag)? Each
provider extra also has a matching file under
[`requirements/`](https://github.com/Geeks-Trident-LLC/textfsm-ai/tree/main/requirements):

```bash
pip install textfsm-ai
pip install -r requirements/requirements-anthropic.txt
```

One file per provider SDK: `requirements-openai.txt` (also covers every
OpenAI-compatible provider), `requirements-anthropic.txt`,
`requirements-gemini.txt`, `requirements-vertexai.txt`,
`requirements-azure.txt`, `requirements-mistral.txt`,
`requirements-bedrock.txt`, `requirements-cohere.txt`,
`requirements-oci.txt`. Each contains exactly the same package spec as
the matching `pyproject.toml` extra - install as many as you need with
multiple `-r` flags. There's no `requirements-all.txt`; use
`pip install textfsm-ai[all]` (or `-e ".[all]"` for dev, see below) for
that.

## Verify installation

```bash
python -c "import textfsm_ai; print(textfsm_ai.__version__)"
```

## Optional: Install development tools

```bash
pip install -e ".[all,dev]"
```

This includes every provider SDK plus:

- pytest + pytest-cov
- ruff, black, mypy

Only working on one or two providers and don't want the rest installed?
Combine `-e .`, `dev`, and just the `requirements/` file(s) you need
instead of `[all,dev]`:

```bash
pip install -e ".[dev]"
pip install -r requirements/requirements-anthropic.txt
pip install -r requirements/requirements-openai.txt
```

Or, for a single provider, `requirements/dev-<provider>.txt` does both
steps in one file (`-e .[dev]` plus that provider's SDK):

```bash
pip install -r requirements/dev-anthropic.txt
```

See [`requirements/README.md`](https://github.com/Geeks-Trident-LLC/textfsm-ai/blob/main/requirements/README.md)
for the full set and how the two styles differ.

For docs tooling (mkdocs + mkdocstrings), see
[CONTRIBUTING.md](https://github.com/Geeks-Trident-LLC/textfsm-ai/blob/main/CONTRIBUTING.md).
