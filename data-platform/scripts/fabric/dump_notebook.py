#!/usr/bin/env python3
"""Read-only inspector for Jupyter/Fabric ``.ipynb`` notebooks.

Prints each cell's type and source so a notebook can be reviewed without
opening it in an editor. This script never writes, uploads, or executes
anything — it only reads the file and prints to stdout, so it is safe to
allow-list.

Usage:
    python dump_notebook.py <path-to.ipynb> [--code|--markdown]

Options:
    --code       Only print code cells.
    --markdown   Only print markdown cells.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def dump(path: Path, only: str | None) -> int:
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 1
    nb = json.loads(path.read_text(encoding="utf-8"))
    for i, cell in enumerate(nb.get("cells", [])):
        ctype = cell.get("cell_type", "?")
        if only and ctype != only:
            continue
        print(f"--- cell {i} [{ctype}] ---")
        print("".join(cell.get("source", [])))
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only .ipynb cell dumper.")
    p.add_argument("path", help="Path to the .ipynb file")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--code", action="store_const", const="code", dest="only")
    g.add_argument("--markdown", action="store_const", const="markdown", dest="only")
    ns = p.parse_args(argv if argv is not None else sys.argv[1:])
    # Notebook cells often contain non-cp1252 characters (arrows, dashes).
    # Force UTF-8 stdout so this read-only dump never crashes on a Windows
    # console whose default code page cannot encode them.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    return dump(Path(ns.path), ns.only)


if __name__ == "__main__":
    sys.exit(main())
