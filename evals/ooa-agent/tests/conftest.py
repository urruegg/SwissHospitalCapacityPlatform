"""Pytest bootstrap for the ooa-agent eval tests — puts ``evals/`` on sys.path
so ``from lib import harness`` resolves.
"""

import sys
from pathlib import Path

EVALS_ROOT = Path(__file__).resolve().parents[2]
if str(EVALS_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALS_ROOT))
