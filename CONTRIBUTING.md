# Contributing to textfsm-ai

Thank you for your interest in contributing!  
This project values clarity, modularity, and professional developer experience.

---

## 🧱 Development Setup

Clone the repository:

```bash
git clone https://github.com/Geeks-Trident-LLC/textfsm-ai.git
cd textfsm-ai
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Install development dependencies:

```bash
pip install -e ".[all]"
```

---

## 🧪 Running Tests

```bash
pytest
```

Coverage:

```bash
pytest --cov=textfsm_ai
```

---

## 🧹 Linting

```bash
ruff check .
```

Auto-fix:

```bash
ruff check . --fix
```

---

## 🧩 Code Style

- Use intention‑revealing names
- Prefer early returns
- Group related logic
- Avoid noisy exception handling
- Keep CLI text clean and professional
- Keep documentation Markdown‑friendly

---

## 🔀 Branching Model

- `main` — stable releases
- `develop` — active development
- `feature/<name>` — new features
- `fix/<name>` — bug fixes

---

## 🔧 Pull Requests

Please ensure:

- PRs are focused and minimal
- Tests cover new behavior
- Documentation is updated
- Commit messages are clear and conventional

---

## 📬 Reporting Issues

Include:

- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs or stack traces

---

Thank you for helping improve **textfsm-ai**!
