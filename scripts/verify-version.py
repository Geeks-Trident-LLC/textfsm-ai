#!/usr/bin/env python3
"""
Verifies that version numbers match across:
- pyproject.toml
- textfsm_ai/__init__.py
- .bumpversion.cfg

Exit code:
0 = OK
1 = mismatch
"""

import re
import sys
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]

def extract_init_version():
    text = (ROOT / "textfsm_ai" / "__init__.py").read_text()
    return re.search(r'__version__ = "(.+?)"', text).group(1)

def extract_pyproject_version():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    return data["project"]["version"]

def extract_cfg_version():
    text = (ROOT / ".bumpversion.cfg").read_text()
    return re.search(r"current_version = (.+)", text).group(1).strip()

def main():
    init_v = extract_init_version()
    proj_v = extract_pyproject_version()
    cfg_v = extract_cfg_version()

    if len({init_v, proj_v, cfg_v}) == 1:
        print(f"Version OK: {init_v}")
        return 0

    print("Version mismatch detected:")
    print(f"  __init__.py:        {init_v}")
    print(f"  pyproject.toml:     {proj_v}")
    print(f"  .bumpversion.cfg:   {cfg_v}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
