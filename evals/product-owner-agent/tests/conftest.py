"""Pytest bootstrap for the PO Agent eval harness tests.

Puts ``evals/product-owner-agent/`` on sys.path so ``import run_evals``
resolves. (The existing schema test uses no imports from here, so this
is additive and non-breaking.)
"""

import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1]
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))
