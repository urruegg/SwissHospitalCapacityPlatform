"""Shared pytest fixtures / path wiring for the WS-A corpus tests.

Adds the corpus module directory to sys.path so `import phi_gate` etc. resolve
without an installed package (mirrors the external-signals script convention).
"""
from __future__ import annotations

import sys
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parents[1]
if str(CORPUS_DIR) not in sys.path:
    sys.path.insert(0, str(CORPUS_DIR))
