"""
Ensures version is consistent across:
- pyproject.toml
- textfsm_ai/__init__.py
- .bumpversion.cfg
"""

import re
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_version_consistency():
    # Load version from __init__.py
    init_file = ROOT / "textfsm_ai" / "__init__.py"
    init_version = re.search(r'__version__ = "(.+?)"', init_file.read_text()).group(1)

    # Load version from pyproject.toml
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    pyproject_version = pyproject["project"]["version"]

    # Load version from .bumpversion.cfg
    cfg_file = ROOT / ".bumpversion.cfg"
    cfg_version = (
        re.search(r"current_version = (.+)", cfg_file.read_text()).group(1).strip()
    )

    assert init_version == pyproject_version == cfg_version
