# OpenAI provider

**Prefix:** `openai/`

## Configuration

Environment variables:

- `OPENAI_API_KEY`

YAML:

```yaml
providers:
  - name: openai
    type: openai
    params:
      api_key: ${OPENAI_API_KEY}
```

## Example models

- `openai/gpt-4o-mini`
- `openai/gpt-4o`

## Example usage

```bash
textfsm-ai providers test \
  --model openai/gpt-4o-mini \
  --prompt "Extract fields from this CLI output"
```
```

Repeat similarly for:

- `docs/providers/anthropic.md`
- `docs/providers/gemini.md`
- `docs/providers/azure.md`

Each with:

- prefix  
- required env vars  
- example YAML config  
- example models  
- example CLI command  
