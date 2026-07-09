"""RLS-proof pill test harness for the Power BI Demoable Redesign (M1).

Reads the identity matrix (``rls_test_matrix.yaml``) and, for each identity,
asserts the ``[Effective Viewing Label]`` measure returns the expected pill
wording (design spec §7 / §10.2).

M1 scaffold: because a live Direct Lake DAX endpoint is not wired in this
environment, the harness *simulates* the ``[Effective Viewing Label]`` DAX by
replaying the same logic against the ``data/synthetic/personas.csv`` seed. This
catches seed/matrix drift and pins the pill contract. When Foundry/Fabric DAX
exec secrets are available (Sprint 11 dependency), swap ``simulate_pill`` for a
live evaluation — see the ``TODO: wire live DAX exec`` marker below.

Usage:
    python data-platform/scripts/rls_test.py
    python data-platform/scripts/rls_test.py --matrix <path> --personas <path>

Exit 0 = all rows PASS, 1 = any row FAIL or input error.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

DEFAULT_MATRIX = Path("data-platform/scripts/rls_test_matrix.yaml")
DEFAULT_PERSONAS = Path("data/synthetic/personas.csv")

DEMO_ROLES = {"HCC.DemoOperator", "HCC.SuperAdmin"}


def load_personas(path: Path) -> dict[str, dict[str, str]]:
    """Return {upn: {display_name, app_role, default_hospital}}."""
    with path.open(newline="", encoding="utf-8") as fh:
        return {row["upn"]: row for row in csv.DictReader(fh)}


def load_matrix(path: Path) -> list[dict[str, str]]:
    """Parse the flat pill matrix.

    Uses PyYAML when available; otherwise falls back to a minimal parser for the
    known ``matrix:`` list-of-mappings shape so the harness stays dependency-free.
    """
    text = path.read_text(encoding="utf-8")
    try:  # pragma: no cover - exercised only when PyYAML is installed
        import yaml

        data = yaml.safe_load(text)
        return list(data.get("matrix", []))
    except ImportError:
        return _parse_matrix_minimal(text)


def _parse_matrix_minimal(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        line = raw.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            current = {}
            rows.append(current)
            stripped = stripped[2:].strip()
        if current is None or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        current[key.strip()] = value.strip().strip('"')
    return rows


def simulate_pill(persona: dict[str, str], slicer_selection: str | None) -> str:
    """Replay the [Effective Viewing Label] DAX against a persona seed row.

    TODO: wire live DAX exec — replace this simulation with a real evaluation of
    the [Effective Viewing Label] measure via the semantic-model REST API once
    Fabric DAX-exec credentials are available.
    """
    role = persona["app_role"]
    is_demo = role in DEMO_ROLES
    if is_demo:
        hospital = slicer_selection or persona["default_hospital"]
    else:
        hospital = persona["default_hospital"]
    base = f"Viewing: {hospital} • {role}"
    return f"{base} (SIT demo override)" if is_demo else base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RLS-proof pill test harness (M1 scaffold).")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--personas", type=Path, default=DEFAULT_PERSONAS)
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Report path (accepted for workflow parity; not used by the M1 scaffold).",
    )
    args = parser.parse_args(argv)

    if not args.matrix.exists():
        print(f"FAIL: matrix {args.matrix} not found")
        return 1
    if not args.personas.exists():
        print(f"FAIL: personas {args.personas} not found")
        return 1

    personas = load_personas(args.personas)
    matrix = load_matrix(args.matrix)
    if not matrix:
        print("FAIL: empty test matrix")
        return 1

    failures = 0
    for row in matrix:
        upn = row.get("upn", "")
        expected = row.get("expected_pill", "")
        persona = personas.get(upn)
        if persona is None:
            print(f"FAIL {upn}: no matching row in {args.personas}")
            failures += 1
            continue
        actual = simulate_pill(persona, row.get("slicer_selection"))
        if actual == expected:
            print(f"PASS {upn}: {actual}")
        else:
            print(f"FAIL {upn}: expected {expected!r}, got {actual!r}")
            failures += 1

    total = len(matrix)
    print(f"\n{total - failures}/{total} identities PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
