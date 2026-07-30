"""Pytest bootstrap for the BVA Agent eval harness tests.

Puts ``evals/bva-agent/`` on sys.path so future harness imports resolve.
The schema conformance test does not import from here; this is a minimal
non-breaking shim matching the product-owner-agent test layout.
"""

import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1]
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))
