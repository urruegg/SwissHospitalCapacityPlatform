"""Sprint 23 WS-B3 -- synthetic seeder for the skills-evidence lane.

Runs each WS-B2 connector over its committed fixture, normalizes the output into a
single ``DC-SKILL-EVIDENCE-v1`` envelope, and either prints it / writes it to a
path, or (``--dry-run``) validates it against the committed JSON schema and prints
the record count. Dependency-free: schema validation is a manual required-key /
enum check so no ``jsonschema`` install is needed.

This seeder is the payload a **Container Apps job** runs to drop a batch extract
into the ADLS landing zone (design D4) -- it is never wired into a GitHub
workflow. Synthetic / no-PHI only (ADR-0013 / ADR-0016).

Usage::

    cd data-platform/scripts/skills-evidence
    PYTHONPATH=. python skills_evidence_synth.py --dry-run
    PYTHONPATH=. python skills_evidence_synth.py --output ../../../data/synthetic/skills-evidence/seed.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from connectors.successfactors import SuccessFactorsConnector
from connectors.lms import LmsConnector
from connectors.skills_manager import SkillsManagerConnector
from connectors.work_id import WorkIdConnector
from dedup import collapse
from normalize import envelope

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
FIXTURES_DIR = _HERE / "tests" / "fixtures"
SCHEMA_PATH = (
    _REPO_ROOT / "data" / "synthetic" / "schema" / "dc-skill-evidence-v1.schema.json"
)
DEFAULT_DATASET_ID = "DS-SKILL-EVIDENCE-synthetic-seed"

# (connector, fixture filename) -- mirrors tests/test_connectors.py.
_CONNECTORS = [
    (SuccessFactorsConnector(), "successfactors.json"),
    (LmsConnector(), "lms.json"),
    (SkillsManagerConnector(), "skills_manager.json"),
    (WorkIdConnector(), "work_id.json"),
]


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def build_records(*, dedupe: bool = True) -> list[dict]:
    """Run every connector over its fixture and return the merged record list."""
    records: list[dict] = []
    for connector, fixture in _CONNECTORS:
        records.extend(connector.parse(_load_fixture(fixture)))
    return collapse(records) if dedupe else records


def build_envelope(dataset_id: str = DEFAULT_DATASET_ID, *, dedupe: bool = True) -> dict:
    return envelope(build_records(dedupe=dedupe), dataset_id=dataset_id)


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
        errors.append(f"contractId {doc.get('contractId')!r} not in {expected_contract}")

    rec_schema = schema["properties"]["records"]["items"]
    rec_required = set(rec_schema.get("required", []))
    rec_props = rec_schema.get("properties", {})
    enums = {k: v["enum"] for k, v in rec_props.items() if "enum" in v}

    records = doc.get("records", [])
    if not records:
        errors.append("envelope has no records")
    for i, rec in enumerate(records):
        missing = rec_required - set(rec)
        if missing:
            errors.append(f"record[{i}] {rec.get('evidenceId')!r} missing {sorted(missing)}")
        for field, allowed in enums.items():
            if field in rec and rec[field] not in allowed:
                errors.append(
                    f"record[{i}] {rec.get('evidenceId')!r} {field}={rec[field]!r} not in {allowed}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic DC-SKILL-EVIDENCE-v1 seeder (runs WS-B2 connectors over fixtures)."
    )
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    parser.add_argument("--output", type=Path, default=None,
                        help="Write the envelope JSON here (default: stdout).")
    parser.add_argument("--no-dedupe", action="store_true",
                        help="Skip de-duplication (emit every raw record).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate against the schema and print the record count; write nothing.")
    args = parser.parse_args(argv)

    doc = build_envelope(args.dataset_id, dedupe=not args.no_dedupe)
    errors = validate(doc)
    if errors:
        for err in errors:
            print(f"INVALID: {err}", file=sys.stderr)
        return 1

    count = len(doc["records"])
    if args.dry_run:
        print(f"OK: {count} DC-SKILL-EVIDENCE-v1 records validated against schema.")
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
