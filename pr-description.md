## Summary

This PR prepares the v0.1.20 release with improvements to the CI pipeline and documentation assets.

## Changes

### CI / Release Workflow
- Updated PyPI publish action inputs to kebab-case to align with the GitHub Actions schema.
- Switched to the correct `pypa/gh-action-pypi-publish@release/v1` tag for trusted publishing.
- Removed legacy authentication fields (`user`, `password`) to ensure OIDC-based publishing works reliably.

### Documentation
- Improved `banner.svg` with better text alignment and a clean black outline for improved readability.

## Impact

- Trusted publishing to PyPI now works with the correct action tag and schema.
- Documentation visuals are cleaner and more consistent with the project’s branding.
- No runtime or API changes.
