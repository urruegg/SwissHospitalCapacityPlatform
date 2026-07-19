#!/usr/bin/env python3
"""Assert the produced gold table set covers the capacity-dashboard contract.

Contract = the non-bva table names in
data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/.
Produced = a table list (one name per line) captured after a medallion run,
passed via --produced <file>. Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TABLES_DIR = (REPO_ROOT / "data-platform" / "reports" /
              "capacity-dashboard.SemanticModel" / "definition" / "tables")


def contract_tables(tables_dir: Path) -> set[str]:
    names = set()
    for tmdl in tables_dir.glob("*.tmdl"):
        stem = tmdl.stem
        if stem.startswith("bva_"):
            continue
        names.add(stem)
    return names


def missing_tables(contract: set[str], produced: set[str]) -> set[str]:
    return contract - produced


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--produced", required=True,
                   help="File with one produced gold table name per line")
    p.add_argument("--tables-dir", default=str(TABLES_DIR))
    ns = p.parse_args(argv if argv is not None else sys.argv[1:])

    contract = contract_tables(Path(ns.tables_dir))
    produced = {ln.strip() for ln in Path(ns.produced).read_text(encoding="utf-8").splitlines() if ln.strip()}
    missing = missing_tables(contract, produced)
    if missing:
        print("GOLD-SCHEMA PARITY FAILED. Missing from produced gold:")
        for m in sorted(missing):
            print(f"  - {m}")
        return 1
    print(f"OK: gold parity ({len(contract)} contract tables covered).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
