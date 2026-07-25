"""Sprint 23 WS-A4 -- synthetic seeder for the near-real-time skills-events lane.

Parses the three committed event fixtures (credential-expiry, consent-grant-or-revoke,
newly-confirmed-assertion) into a single ``DC-SKILL-EVENT-v1`` envelope, and either
prints it / writes it to a path, or (``--dry-run``) validates it against the committed
JSON schema and prints the record count. Dependency-free: schema validation is a manual
required-key / enum check so no ``jsonschema`` install is needed.

This seeder is the payload a **Container Apps service** runs to publish event
envelopes to the WS-A4 Eventstream lane (design D4) -- it is never wired into a
GitHub workflow. The Eventstream routes by the ``eventKind`` message property and
lands raw envelopes at ``Files/bronze/skills-events/``; gating is downstream in the
silver notebook. Synthetic / no-PHI only (ADR-0013 / ADR-0016).

Usage::

    cd data-platform/scripts/skills-events
    PYTHONPATH=. python skill_events_synth.py --dry-run
    PYTHONPATH=. python skill_events_synth.py --output ../../../data/synthetic/skills-events/seed.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from normalize import build_event, envelope

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
FIXTURES_DIR = _HERE / "tests" / "fixtures"
SCHEMA_PATH = (
    _REPO_ROOT / "data" / "synthetic" / "schema" / "dc-skill-event-v1.schema.json"
)
DEFAULT_DATASET_ID = "DS-SKILL-EVENT-synthetic-seed"
CONNECTOR_VERSION = "skills-events-synth/1.0.0"
LICENCE = "synthetic-internal"

# fixture filename per event kind.
_FIXTURES = {
    "credential-expiry": "credential_expiry.json",
    "consent-grant-or-revoke": "consent_events.json",
    "newly-confirmed-assertion": "confirmed_assertions.json",
}


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _parse_credential_expiry(doc: dict) -> list[dict]:
    out = []
    for raw in doc.get("expirations", []):
        out.append(build_event(
            event_id=raw["credentialId"],
            event_kind="credential-expiry",
            external_system="lms",
            source_mode="simulated",
            trust_tier="A",
            external_person_ref=raw["learnerRef"],
            external_skill_code=raw["courseCode"],
            external_skill_label=raw.get("courseTitle"),
            credential_valid=bool(raw.get("stillValid", False)),
            effective_at=raw["expiredOn"],
            connector_version=CONNECTOR_VERSION,
            licence=LICENCE,
            raw=raw,
        ))
    return out


def _parse_consent(doc: dict) -> list[dict]:
    out = []
    for raw in doc.get("decisions", []):
        action = raw["action"]
        granted = action == "grant"
        out.append(build_event(
            event_id=raw["decisionId"],
            event_kind="consent-grant-or-revoke",
            external_system="work_id",
            source_mode="simulated",
            trust_tier="C",
            external_person_ref=raw["workIdRef"],
            external_skill_code=raw["skillCode"],
            external_skill_label=raw.get("skillLabel"),
            # GLN promotion + scope are carried ONLY on grant; revoke clears both.
            worker_gln=raw.get("workerGln") if granted else None,
            consent_action=action,
            consent_scope=raw.get("consentScope") if granted else None,
            effective_at=raw["decidedAt"],
            connector_version=CONNECTOR_VERSION,
            licence=LICENCE,
            raw=raw,
        ))
    return out


def _parse_confirmed(doc: dict) -> list[dict]:
    out = []
    for raw in doc.get("confirmations", []):
        out.append(build_event(
            event_id=raw["confirmationId"],
            event_kind="newly-confirmed-assertion",
            external_system="successfactors",
            source_mode="simulated",
            trust_tier="A",
            external_person_ref=raw["employeeRef"],
            external_skill_code=raw["skillCode"],
            external_skill_label=raw.get("skillLabel"),
            confirmed=True,
            effective_at=raw["confirmedAt"],
            connector_version=CONNECTOR_VERSION,
            licence=LICENCE,
            raw=raw,
        ))
    return out


_PARSERS = {
    "credential-expiry": _parse_credential_expiry,
    "consent-grant-or-revoke": _parse_consent,
    "newly-confirmed-assertion": _parse_confirmed,
}


def build_records() -> list[dict]:
    """Parse every event fixture and return the merged DC-SKILL-EVENT-v1 record list."""
    records: list[dict] = []
    for kind, fixture in _FIXTURES.items():
        records.extend(_PARSERS[kind](_load_fixture(fixture)))
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
            errors.append(f"record[{i}] {rec.get('eventId')!r} missing {sorted(missing)}")
        for field, allowed in enums.items():
            if field in rec and rec[field] not in allowed:
                errors.append(
                    f"record[{i}] {rec.get('eventId')!r} {field}={rec[field]!r} not in {allowed}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic DC-SKILL-EVENT-v1 seeder (parses the three event fixtures)."
    )
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    parser.add_argument("--output", type=Path, default=None,
                        help="Write the envelope JSON here (default: stdout).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate against the schema and print the record count; write nothing.")
    args = parser.parse_args(argv)

    doc = build_envelope(args.dataset_id)
    errors = validate(doc)
    if errors:
        for err in errors:
            print(f"INVALID: {err}", file=sys.stderr)
        return 1

    count = len(doc["records"])
    if args.dry_run:
        print(f"OK: {count} DC-SKILL-EVENT-v1 records validated against schema.")
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
