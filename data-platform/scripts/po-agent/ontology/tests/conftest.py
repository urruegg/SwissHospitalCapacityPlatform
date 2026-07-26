"""Pytest bootstrap: put the ontology module dir on sys.path."""

import sys
from pathlib import Path

ONTOLOGY_DIR = Path(__file__).resolve().parents[1]
if str(ONTOLOGY_DIR) not in sys.path:
    sys.path.insert(0, str(ONTOLOGY_DIR))
