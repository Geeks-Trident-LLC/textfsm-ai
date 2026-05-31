"""
Ensures version is consistent across:
- pyproject.toml
- textfsm_ai/__init__.py
- .bumpversion.cfg
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_version_from_pyproject():
    text = (ROOT / "pyproject.toml").read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("Version not found in pyproject.toml")
    return match.group(1)


def test_version_consistency():
    # Load version from __init__.py
    init_file = ROOT / "textfsm_ai" / "__init__.py"
    init_version = re.search(r'__version__ = "(.+?)"', init_file.read_text()).group(1)

    # Load version from pyproject.toml (regex, no tomllib)
    pyproject_version = extract_version_from_pyproject()

    # Load version from .bumpversion.cfg
    cfg_file = ROOT / ".bumpversion.cfg"
    cfg_version = (
        re.search(r"current_version = (.+)", cfg_file.read_text()).group(1).strip()
    )

    assert init_version == pyproject_version == cfg_version
