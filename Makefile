VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

# -----------------------------
# TestPyPI Release
# -----------------------------
release-test:
    @echo "Releasing to TestPyPI version $(VERSION)"
    @if git rev-parse "v$(VERSION)-test" >/dev/null 2>&1; then \
        echo "ERROR: Tag v$(VERSION)-test already exists."; \
        exit 1; \
    fi
    git tag v$(VERSION)-test
    git push origin v$(VERSION)-test

# -----------------------------
# Production PyPI Release
# -----------------------------
release-prod:
    @if [ "$(CURRENT_BRANCH)" != "main" ]; then \
        echo "ERROR: Must be on main to release to PyPI."; \
        exit 1; \
    fi
    @if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
        echo "ERROR: Tag v$(VERSION) already exists."; \
        exit 1; \
    fi
    @echo "Releasing version $(VERSION) to PyPI"
    git tag v$(VERSION)
    git push origin v$(VERSION)
    gh release create v$(VERSION) --generate-notes

# Optional alias
release: release-prod

# -----------------------------
# Version bumping
# -----------------------------
bump-patch:
    bump2version patch

bump-minor:
    bump2version minor

bump-major:
    bump2version major


tox:
    tox

tox-lint:
    tox -e lint

tox-typecheck:
    tox -e typecheck
