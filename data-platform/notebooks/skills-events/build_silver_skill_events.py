"""Sprint 23 WS-A4 -- Silver transform (PHI/consent gate) for the skills-events lane.

Splits raw DC-SKILL-EVENT-v1 events into a clean ``silver.skill_events`` stream and
a ``silver.skill_events_quarantine`` stream, and enforces the consent gate the WS-A4
Eventstream module defers to the silver notebook (its manifest records
``phiGateEnforcedBy: silver-skills-events-notebook``):

* **Validation / deny-by-default** -- an event is kept only when its ``eventKind`` is
  one of the three allowed kinds, all required contract fields are present, and its
  consent shape is coherent (see ``consent_shape_error``). Everything else is
  quarantined for audit, never silently dropped.
* **Consent revocation removes the GLN promotion** -- for a ``revoke`` decision the
  silver gate defensively clears ``workerGln`` and ``consentScope`` even if an
  upstream payload still carried them, so a revoked worker can never be promoted on
  the next load (COMPLIANCE.md sec Sprint 23; FR-SKILL-003).

The pure functions here are unit-tested without Spark (see
``tests/test_skill_events_pure.py``), following the ``external-signals`` pattern.
The seeder package is loaded by path so this file stays importable from the notebook
directory during offline tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "skills-events"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from normalize import EVENT_KINDS  # noqa: E402 - path injected above

SILVER_SCHEMA = "silver"
SILVER_TABLE = "skill_events"
SILVER_QUARANTINE_TABLE = "skill_events_quarantine"
BRONZE_TABLE = "bronze.skill_events_raw"

_REQUIRED = (
    "eventId", "eventKind", "externalSystem", "sourceMode", "trustTier",
    "externalPersonRef", "externalSkillCode", "effectiveAt",
)


def consent_shape_error(rec: dict) -> str | None:
    """Return an error string if a consent event's shape is incoherent, else None.

    A ``grant`` must carry both a ``workerGln`` and a ``consentScope`` (the promotion
    key + the consented purpose). A ``revoke`` must not assert a promotion. Non-consent
    events must not carry a ``consentAction``.
    """
    kind = rec.get("eventKind")
    action = rec.get("consentAction")
    if kind == "consent-grant-or-revoke":
        if action not in ("grant", "revoke"):
            return f"consent event {rec.get('eventId')!r} has consentAction={action!r}"
        if action == "grant" and not (rec.get("workerGln") and rec.get("consentScope")):
            return f"consent grant {rec.get('eventId')!r} missing workerGln/consentScope"
        return None
    if action is not None:
        return f"non-consent event {rec.get('eventId')!r} carries consentAction={action!r}"
    return None


def validate_event(rec: dict) -> list[str]:
    """Return a list of validation errors for one event (empty=valid)."""
    errors: list[str] = []
    missing = [f for f in _REQUIRED if rec.get(f) in (None, "")]
    if missing:
        errors.append(f"event {rec.get('eventId')!r} missing {missing}")
    if rec.get("eventKind") not in EVENT_KINDS:
        errors.append(f"event {rec.get('eventId')!r} bad eventKind={rec.get('eventKind')!r}")
    shape = consent_shape_error(rec)
    if shape:
        errors.append(shape)
    return errors


def enforce_consent_gate(rec: dict) -> dict:
    """Return a copy of the event with the consent-revocation invariant enforced.

    On a ``revoke`` the GLN promotion and consented scope are cleared regardless of
    what the upstream payload carried, so a revoked worker is never promoted.
    """
    if rec.get("eventKind") == "consent-grant-or-revoke" and rec.get("consentAction") == "revoke":
        out = dict(rec)
        out["workerGln"] = None
        out["consentScope"] = None
        return out
    return rec


def split_quarantine(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Partition events into (kept, quarantined).

    ``kept`` retains only events that pass ``validate_event``, with the consent gate
    applied; everything else is quarantined for audit (deny-by-default).
    """
    kept: list[dict] = []
    quarantined: list[dict] = []
    for rec in records:
        if validate_event(rec):
            quarantined.append(rec)
        else:
            kept.append(enforce_consent_gate(rec))
    return kept, quarantined


def _write(df, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{SILVER_SCHEMA}.{table}")
    print(f"silver: wrote {SILVER_SCHEMA}.{table} ({df.count()} rows)")


def build_silver_skill_events(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read Bronze skill_events_raw, gate, and write silver.skill_events + quarantine."""
    df = spark.read.table(BRONZE_TABLE)
    schema = df.schema
    rows = [r.asDict(recursive=True) for r in df.collect()]
    kept, quarantined = split_quarantine(rows)
    _write(spark.createDataFrame(kept, schema), SILVER_TABLE)
    _write(spark.createDataFrame(quarantined, schema), SILVER_QUARANTINE_TABLE)


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Reads Bronze, writes silver.skill_events + quarantine."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided

    build_silver_skill_events(SparkSession.builder.getOrCreate())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
