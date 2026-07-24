"""Sprint 21 M3.2 — synthetic seeder for the Trusted External Signals lane.

Runs each M2 connector over its committed fixture, normalizes the output into a
single ``DC-EXT-SIGNAL-v1`` envelope, and either prints it to stdout / writes it
to a path, or (``--dry-run``) validates it against the committed JSON schema and
prints the record count. Dependency-free (schema validation is a manual
required-key check so no ``jsonschema`` install is needed); ``pyarrow`` is
optional and only used for the ``--parquet`` convenience output.

Synthetic-only (ADR-0013 / ADR-0016). No PHI — the fixtures carry public
authority hazard warnings.

Usage::

    cd data-platform/scripts/external-signals
    PYTHONPATH=. python3 signals_synth.py --dry-run
    PYTHONPATH=. python3 signals_synth.py --output ../../../data/synthetic/external-signals/seed.json
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from providers.registry import discover
from normalize import envelope

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
FIXTURES_DIR = _HERE / "tests" / "fixtures"
SCHEMA_PATH = (
    _REPO_ROOT / "data" / "synthetic" / "schema" / "dc-ext-signal-v1.schema.json"
)
DEFAULT_DATASET_ID = "ext-signal-synthetic-seed"

# fixture filename per provider (raw payloads live in tests/fixtures)
_PROVIDER_FIXTURES = {
    "meteoswiss": "meteoswiss_heat.json",
    "sed": "sed_quake.json",
    "alertswiss": "alertswiss_cap.json",
    "bag": "bag_rsv.json",
}


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def build_records() -> list[dict]:
    """Run every provider parse over its fixture and return the merged record list."""
    records: list[dict] = []
    for spec in discover():
        fixture = _PROVIDER_FIXTURES.get(spec.source_id)
        if not fixture:
            continue  # simulator/internal-only providers seeded elsewhere
        parse = importlib.import_module(f"providers.{spec.source_id}.parse").parse
        records.extend(parse(_load_fixture(fixture)))
    return records


def build_envelope(dataset_id: str = DEFAULT_DATASET_ID) -> dict:
    return envelope(build_records(), dataset_id=dataset_id)


def validate(doc: dict) -> list[str]:
    """Dependency-free schema check. Returns a list of error strings (empty=ok)."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    env_required = set(schema.get("required", []))
    missing_env = env_required - set(doc)
    if missing_env:
        errors.append(f"envelope missing keys: {sorted(missing_env)}")

    expected_contract = schema["properties"]["contractId"].get("enum", [])
    if expected_contract and doc.get("contractId") not in expected_contract:
        errors.append(
            f"contractId {doc.get('contractId')!r} not in {expected_contract}"
        )

    rec_required = set(schema["properties"]["records"]["items"].get("required", []))
    records = doc.get("records", [])
    if not records:
        errors.append("envelope has no records")
    for i, rec in enumerate(records):
        missing = rec_required - set(rec)
        if missing:
            errors.append(f"record[{i}] {rec.get('signalId')!r} missing {sorted(missing)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic DC-EXT-SIGNAL-v1 seeder (runs M2 connectors over fixtures)."
    )
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Write the envelope JSON here (default: stdout).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate against the schema and print the record count; write nothing.",
    )
    args = parser.parse_args(argv)

    doc = build_envelope(args.dataset_id)
    errors = validate(doc)
    if errors:
        for err in errors:
            print(f"INVALID: {err}", file=sys.stderr)
        return 1

    count = len(doc["records"])
    if args.dry_run:
        print(f"OK: {count} DC-EXT-SIGNAL-v1 records validated against schema.")
        return 0

    payload = json.dumps(doc, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"OK: wrote {count} records to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
