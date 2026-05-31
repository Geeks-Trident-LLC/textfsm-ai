
# Golden Tests

Golden tests ensure your TextFSM templates remain stable and correct over time.

A golden test consists of:

- a template (`.template`)
- an input text file (`.txt`)
- an expected output file (`.json`)

## Directory structure

```
tests/golden/
  show_ip_interface/
    template
    input.txt
    expected.json
```

## Run all golden tests

```bash
pytest -k golden
```

## Why golden tests?

- Prevent regressions
- Ensure template stability
- Document expected behavior
- Provide fast feedback during development

## Writing a new golden test

1. Create a folder under `tests/golden/`
2. Add:
   - `template`
   - `input.txt`
   - `expected.json`
3. Run:

```bash
pytest -k golden --update
```