VERSION := $(shell python - <<'EOF'
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
EOF
)

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

    @echo "Checking local tag v$(VERSION)..."
    @if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
        echo "Tag v$(VERSION) already exists locally. Skipping tag creation."; \
    else \
        echo "Creating local tag v$(VERSION)"; \
        git tag v$(VERSION); \
    fi

    @echo "Checking remote tag v$(VERSION)..."
    @if git ls-remote --tags origin "v$(VERSION)" | grep "v$(VERSION)" >/dev/null; then \
        echo "Tag v$(VERSION) already exists on origin. Skipping push."; \
    else \
        echo "Pushing tag v$(VERSION) to origin"; \
        git push origin v$(VERSION); \
    fi

    @echo "Checking GitHub Release for v$(VERSION)..."
    @if gh release view v$(VERSION) >/dev/null 2>&1; then \
        echo "GitHub Release v$(VERSION) already exists. Updating notes."; \
        gh release edit v$(VERSION) --generate-notes; \
    else \
        echo "Creating GitHub Release v$(VERSION)"; \
        gh release create v$(VERSION) --generate-notes; \
    fi

    @echo "release-prod completed successfully."

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

# -----------------------------
# Tox
# -----------------------------
tox:
    tox

tox-lint:
    tox -e lint

# Remove this if no typecheck env exists
tox-typecheck:
    tox -e typecheck

# -----------------------------
# Version checks
# -----------------------------
verify-version:
    @echo "Checking version consistency..."
    @python scripts/verify-version.py

test-version:
    pytest -q tests/test_version_consistency.py

.PHONY: \
    release-test release-prod release \
    bump-patch bump-minor bump-major \
    tox tox-lint tox-typecheck \
    verify-version test-version
