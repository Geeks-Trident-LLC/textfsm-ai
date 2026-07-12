# textfsm_ai/__init__.py

from pathlib import Path

__version__ = "0.4.1"
version = __version__

BASE_DIR = Path(__file__).resolve().parent


__all__ = ["BASE_DIR", "version", "__version__"]
