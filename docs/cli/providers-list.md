# `textfsm-ai providers list`

List all registered provider types.

## Usage

```bash
textfsm-ai providers list
```

## Example output

```text
openai      (OpenAIProvider)
anthropic   (AnthropicProvider)
gemini      (GeminiProvider)
azure       (AzureOpenAIProvider)
```
```

#### `docs/cli/providers-test.md`

```markdown
# `textfsm-ai providers test`

Send a test prompt through the orchestrator to the appropriate provider.

## Usage

```bash
textfsm-ai providers test \
  --model openai/gpt-4o-mini \
  --prompt "Say hello"
```

Optional:

```bash
textfsm-ai providers test \
  --config ./textfsm_ai.yaml \
  --model anthropic/claude-3-5-sonnet \
  --prompt "Summarize this CLI output"
```
```

#### `docs/cli/providers-info.md`

```markdown
# `textfsm-ai providers info`

Show configuration-related info for a provider (safe fields only).

## Usage

```bash
textfsm-ai providers info --name openai
```

Example output:

```text
Name: openai
Type: openai
Params: {'api_key': '***'}
```
```

#### `docs/cli/orchestrator-route.md`

```markdown
# `textfsm-ai orchestrator route`

Show which provider a model would be routed to.

## Usage

```bash
textfsm-ai orchestrator route --model anthropic/claude-3-5-sonnet
```

Example output:

```text
Model: anthropic/claude-3-5-sonnet
Routed provider: anthropic
```
```

#### `docs/cli/orchestrator-run.md`

```markdown
# `textfsm-ai orchestrator run`

Run a full orchestrator request and print the response.

## Usage

```bash
textfsm-ai orchestrator run \
  --model gemini/gemini-1.5-flash \
  --prompt "Extract fields from this CLI output"
```

Optional config file:

```bash
textfsm-ai orchestrator run \
  --config ./textfsm_ai.yaml \
  --model openai/gpt-4o-mini \
  --prompt "Generate a TextFSM template"
```
```

---

### 6. Example commands for users

```bash
# List providers
textfsm-ai providers list

# Show info for a configured provider
textfsm-ai providers info --name openai

# Test a provider via env-based config
export OPENAI_API_KEY=sk-...
textfsm-ai providers test \
  --model openai/gpt-4o-mini \
  --prompt "Say hello"

# Test routing only
textfsm-ai orchestrator route --model anthropic/claude-3-5-sonnet

# Run full orchestrator call
textfsm-ai orchestrator run \
  --model gemini/gemini-1.5-flash \
  --prompt "Extract fields from this CLI output"
```
