## What’s new in v0.1.20

### 🛠 CI Improvements
- Updated PyPI publish workflow to use kebab-case inputs (`packages-dir`, `verify-metadata`).
- Migrated to the correct `pypa/gh-action-pypi-publish@release/v1` tag for OIDC trusted publishing.
- Removed legacy auth fields to ensure PyPI accepts GitHub’s OIDC token.

### 🎨 Documentation
- Updated `banner.svg` with improved alignment and a subtle black outline for better contrast.

### 📌 Notes
This release contains no functional or API changes. It focuses on stabilizing the release pipeline and improving documentation quality.
