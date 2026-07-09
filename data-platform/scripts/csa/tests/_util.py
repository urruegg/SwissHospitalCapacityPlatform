"""Shared helpers for the CSA script test-suite (dependency-free)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

CSA_DIR = Path(__file__).resolve().parents[1]

# Ensure sibling helpers (_schema_util, _cosmos) import cleanly.
if str(CSA_DIR) not in sys.path:
    sys.path.insert(0, str(CSA_DIR))


def load_script(filename: str) -> ModuleType:
    """Import a hyphenated CSA script by filename (e.g. csa-seed-response-levers.py)."""
    path = CSA_DIR / filename
    mod_name = path.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
