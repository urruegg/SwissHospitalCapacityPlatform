"""Collapse duplicate skills-evidence records to one per person/skill/system.

Mirrors ``external-signals/dedup.py``. Identity is
``externalSystem|externalPersonRef|externalSkillCode`` (see ``normalize.dedup_key``).
When the same person/skill arrives more than once from a source, the
``employer_confirmed`` assertion wins over a ``self``-declared one (higher
assurance floor: L1 > L0). This never promotes above the source's ceiling --
federal-register promotion happens later, at the silver/verification step.
"""
from __future__ import annotations

from normalize import dedup_key

CONFIRM_RANK = {"employer_confirmed": 1, "self": 0}


def collapse(records: list[dict]) -> list[dict]:
    groups: dict[str, dict] = {}
    for rec in records:
        key = dedup_key(rec)
        current = groups.get(key)
        if current is None or _rank(rec) > _rank(current):
            groups[key] = rec
    return list(groups.values())


def _rank(rec: dict) -> int:
    return CONFIRM_RANK.get(rec.get("selfOrConfirmed"), 0)
