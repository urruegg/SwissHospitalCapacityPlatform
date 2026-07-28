"""Pytest bootstrap for the shared evaluator-library tests.

Puts ``evals/`` on sys.path so ``from lib import evaluators`` / ``from lib
import harness`` resolve regardless of the working directory pytest is
invoked from.
"""

import sys
from pathlib import Path

EVALS_ROOT = Path(__file__).resolve().parents[2]
if str(EVALS_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALS_ROOT))
