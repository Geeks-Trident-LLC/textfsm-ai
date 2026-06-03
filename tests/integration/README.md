# Integration Tests

These tests hit real external APIs (DeepSeek, OpenAI, etc.) and are **disabled by default**.

## How to enable

You must set:

- `TEST_REAL=true`
- The provider API key(s)

Powershell set environment variable
```powershell
    $env:TEST_REAL="true"
    $env:DEEPSEEK_API_KEY="your-key"
    $env:OPENAI_API_KEY="your-key"

```

## How to run

```
    pytest -m integration

```
## How it works

- Tests use runtime skip logic (`pytest.skip`) so fixtures still run.
- A session-scoped fixture in `tests/conftest.py` resets TEST_REAL after the session.
- Tests are safe to run without keys; they will be skipped.
