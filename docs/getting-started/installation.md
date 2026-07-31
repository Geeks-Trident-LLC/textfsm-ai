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

For docs tooling (mkdocs + mkdocstrings), see
[CONTRIBUTING.md](https://github.com/Geeks-Trident-LLC/textfsm-ai/blob/main/CONTRIBUTING.md).
