#!/usr/bin/env python3
"""Sprint 16 T3 — seed the CSA `response-levers` Cosmos container.

The response-lever library is a doctrine-aligned mitigation catalogue served
from Cosmos (design spec §4 / §6). This script builds the library, validates it
against `schema/response-levers.schema.json`, and — when Cosmos is configured —
upserts it into the `response-levers` container.

Dry run (no creds): validates and prints a summary, exit 0.
Live run: set CSA_COSMOS_ENDPOINT (RBAC via `az login` / managed identity).

    python3 data-platform/scripts/csa/csa-seed-response-levers.py --dry-run

Every response lever is ADVISORY ONLY (`advisoryOnly: true`) — the csa-agent
never auto-executes a lever (design spec §5 refusal rules).
"""
from __future__ import annotations

import argparse
import re
import sys

from _cosmos import cosmos_configured, upsert_all
from _schema_util import load_schema, validate

# (name, category, doctrineTier, [appliesToResources], description)
# Doctrine grounded in the Swiss Lage model (Normallage / Besondere Lage /
# Ausserordentliche Lage) — Tier 2 = internal reallocation, Tier 3 = external
# escalation / special capability overwhelmed (VKSD Art. 2).
_LEVERS: list[tuple[str, str, int, list[str], str]] = [
    # surge-capacity
    ("Open surge beds in step-down units", "surge-capacity", 2, ["beds", "icu-beds"], "Convert monitored step-down bays into additional inpatient/ICU surge capacity."),
    ("Convert PACU to overflow ICU", "surge-capacity", 2, ["icu-beds", "ventilators"], "Repurpose post-anaesthesia recovery as ventilated overflow ICU."),
    ("Activate field/tent triage area", "surge-capacity", 3, ["beds", "ed-capacity"], "Stand up an external triage/treatment tent when internal space is exhausted."),
    ("Reopen mothballed ward", "surge-capacity", 2, ["beds"], "Recommission a closed ward to add inpatient beds."),
    ("Cohort low-acuity patients to shared bays", "surge-capacity", 2, ["beds"], "Cohort stable low-acuity patients to free single rooms for surge."),
    ("Repurpose day-surgery recovery for inpatients", "surge-capacity", 2, ["beds"], "Use day-surgery recovery space for overnight inpatient boarding."),
    ("Establish decontamination line", "surge-capacity", 3, ["decontamination"], "Set up a decontamination corridor for hazardous/chemical presentations."),
    ("Stand up mass-casualty reception zone", "surge-capacity", 3, ["ed-capacity", "beds"], "Activate a mass-casualty reception and secondary-triage zone."),
    ("Activate burn-surge protocol", "surge-capacity", 3, ["burn-beds", "icu-beds"], "Escalate burn-specific surge capacity and coordinate transfers."),
    ("Open pediatric overflow cohort", "surge-capacity", 2, ["pediatric-beds"], "Cohort a pediatric overflow area for seasonal virus surges (e.g. RSV)."),
    ("Extend recovery-room ventilated capacity", "surge-capacity", 2, ["ventilators", "icu-beds"], "Add ventilated capacity in recovery for short-term critical care."),
    ("Deploy mobile isolation units", "surge-capacity", 3, ["isolation-beds"], "Deploy negative-pressure mobile isolation for infectious surge."),
    # staffing
    ("Recall off-duty clinical staff", "staffing", 2, ["nursing-staff", "physician-staff"], "Recall rostered-off clinicians to cover surge demand."),
    ("Activate on-call reserve roster", "staffing", 2, ["nursing-staff"], "Trigger the standby on-call reserve staffing tier."),
    ("Cancel elective leave", "staffing", 2, ["physician-staff", "nursing-staff"], "Temporarily cancel discretionary leave to raise availability."),
    ("Extend shift length within safe limits", "staffing", 2, ["nursing-staff"], "Extend shifts within fatigue-safe limits to bridge gaps."),
    ("Cross-deploy staff from elective areas", "staffing", 2, ["nursing-staff"], "Redeploy staff from paused elective areas to surge areas."),
    ("Request agency / temp staffing", "staffing", 2, ["nursing-staff"], "Engage agency/temporary clinical staff to backfill."),
    ("Activate mutual-aid staffing agreement", "staffing", 3, ["physician-staff", "nursing-staff"], "Invoke inter-hospital mutual-aid staffing arrangements."),
    ("Deploy critical-care outreach team", "staffing", 2, ["icu-staff"], "Send the critical-care outreach team to support deteriorating ward patients."),
    ("Assign supervising intensivist to expanded ICU", "staffing", 2, ["icu-staff"], "Provide intensivist supervision over expanded ventilated capacity."),
    ("Backfill specialists remotely via telemedicine", "staffing", 2, ["physician-staff"], "Use telemedicine to cover absent specialist cover."),
    ("Establish staff welfare and rest rotation", "staffing", 3, ["nursing-staff"], "Institute welfare, rest and rotation for sustained operations."),
    ("Request military medical support", "staffing", 3, ["physician-staff", "nursing-staff"], "Request Armed Forces medical (Sanität) reinforcement via cantonal command."),
    ("Mobilise Spitex for discharge support", "staffing", 2, ["nursing-staff"], "Engage Spitex/community nursing to enable earlier safe discharge."),
    ("Assign logistics roles to non-clinical staff", "staffing", 2, ["support-staff"], "Free clinicians by assigning runner/logistics roles to support staff."),
    # patient-flow
    ("Accelerate discharge of medically-fit patients", "patient-flow", 2, ["beds"], "Prioritise discharge of medically-fit-for-discharge patients."),
    ("Activate discharge lounge", "patient-flow", 2, ["beds"], "Open a discharge lounge to release beds earlier in the day."),
    ("Divert ambulances to partner sites", "patient-flow", 2, ["ed-capacity"], "Request EMS diversion to partner emergency departments."),
    ("Redirect walk-ins to urgent-care partners", "patient-flow", 2, ["ed-capacity"], "Signpost low-acuity walk-ins to urgent-care/GP partners."),
    ("Defer non-urgent elective admissions", "patient-flow", 2, ["beds", "or-slots"], "Postpone non-urgent elective admissions to protect surge capacity."),
    ("Cancel elective OR list", "patient-flow", 2, ["or-slots", "icu-beds"], "Cancel elective operating lists to free OR, staff and ICU."),
    ("Prioritise OR by clinical urgency", "patient-flow", 2, ["or-slots"], "Re-sequence operating lists by clinical urgency."),
    ("Inter-hospital transfer of stable ICU patients", "patient-flow", 3, ["icu-beds"], "Transfer stable ICU patients to create local capacity."),
    ("Repatriate out-of-canton patients", "patient-flow", 3, ["beds"], "Repatriate out-of-canton patients to their home region."),
    ("Fast-track imaging for surge cohort", "patient-flow", 2, ["imaging"], "Prioritise imaging/diagnostics to unblock the surge cohort."),
    ("Establish rapid-assessment unit at front door", "patient-flow", 2, ["ed-capacity"], "Front-load senior assessment to speed decisions at the door."),
    ("Early senior review to expedite decisions", "patient-flow", 2, ["ed-capacity"], "Bring senior decision-makers forward to reduce dwell time."),
    ("Batch pharmacy dispensing for discharges", "patient-flow", 2, ["pharmacy"], "Batch discharge medications to avoid pharmacy bottlenecks."),
    ("Activate step-down transfer pathway", "patient-flow", 2, ["icu-beds", "beds"], "Move recovering ICU patients to step-down to free critical care."),
    # supply-chain
    ("Draw down ventilator reserve stock", "supply-chain", 2, ["ventilators"], "Deploy the local ventilator reserve to meet demand."),
    ("Request cantonal stockpile release", "supply-chain", 3, ["ventilators", "ppe"], "Request release from the cantonal medical stockpile."),
    ("Activate supplier emergency-order agreement", "supply-chain", 2, ["supplies"], "Trigger emergency/priority supplier ordering."),
    ("Reallocate ventilators across sites", "supply-chain", 3, ["ventilators"], "Rebalance ventilators across the hospital network."),
    ("Conserve consumables via rationing protocol", "supply-chain", 3, ["supplies", "ppe"], "Apply a conservation/rationing protocol for scarce consumables."),
    ("Switch to alternate/substitute devices", "supply-chain", 2, ["ventilators"], "Substitute alternate devices where clinically acceptable."),
    ("Prioritise blood-product allocation", "supply-chain", 3, ["blood"], "Coordinate priority allocation of blood products."),
    ("Request national medical materiel reserve", "supply-chain", 3, ["supplies"], "Request national medical materiel reserve support."),
    ("Secure oxygen supply and bulk delivery", "supply-chain", 2, ["oxygen"], "Secure oxygen supply continuity and expedite bulk delivery."),
    ("Borrow equipment from partner hospitals", "supply-chain", 2, ["ventilators", "supplies"], "Borrow critical equipment from partner facilities."),
    # coordination
    ("Activate Hospital Emergency Operations Centre", "coordination", 2, ["command"], "Stand up the hospital EOC to run the response."),
    ("Escalate to cantonal medical command", "coordination", 3, ["command"], "Escalate to cantonal medical service (KSD) command."),
    ("Notify emergency dispatch of capacity", "coordination", 2, ["command"], "Notify the medical dispatch centre (144) of current capacity."),
    ("Establish inter-canton coordination cell", "coordination", 3, ["command"], "Establish an inter-cantonal coordination cell."),
    ("Convene incident management team", "coordination", 2, ["command"], "Convene the incident management team."),
    ("Declare Besondere Lage per VKSD", "coordination", 2, ["command"], "Formally declare Besondere Lage (Tier 2) per VKSD."),
    ("Declare Ausserordentliche Lage per VKSD", "coordination", 3, ["command"], "Formally declare Ausserordentliche Lage (Tier 3) per VKSD Art. 2."),
    ("Request Rega air-transfer coordination", "coordination", 3, ["transport"], "Coordinate Rega air transfers for critical patients."),
    ("Coordinate with neighbouring-country facilities", "coordination", 3, ["command"], "Coordinate cross-border capacity with neighbouring facilities."),
    ("Activate business-continuity plan", "coordination", 2, ["command"], "Invoke the organisational business-continuity plan."),
    ("Establish common operating picture dashboard", "coordination", 2, ["command"], "Publish a shared common-operating-picture dashboard."),
    ("Assign liaison to cantonal crisis staff", "coordination", 3, ["command"], "Embed a liaison officer with the cantonal crisis staff."),
    # communication
    ("Issue internal staff situation update", "communication", 2, ["communication"], "Send timely internal situation updates to staff."),
    ("Brief patients and families on delays", "communication", 2, ["communication"], "Proactively brief patients/families on expected delays."),
    ("Coordinate public messaging with authorities", "communication", 3, ["communication"], "Align public messaging with cantonal authorities."),
    ("Activate media-liaison protocol", "communication", 3, ["communication"], "Activate the media-liaison protocol for major incidents."),
    ("Notify referrers of admission constraints", "communication", 2, ["communication"], "Inform GPs/referrers of current admission constraints."),
    ("Publish diversion status to EMS partners", "communication", 2, ["communication"], "Publish live diversion status to EMS partners."),
    ("Establish family reunification information line", "communication", 3, ["communication"], "Stand up a family reunification/information line."),
    ("Send scheduled situation reports to command", "communication", 2, ["command", "communication"], "Send scheduled SITREPs to the coordinating command."),
    # continuity
    ("Fail over to backup clinical IT systems", "continuity", 2, ["it-systems"], "Fail clinical systems over to validated backup infrastructure."),
    ("Activate downtime paper procedures", "continuity", 2, ["it-systems"], "Switch to paper downtime procedures during IT outage."),
    ("Isolate affected network segments", "continuity", 3, ["it-systems"], "Isolate compromised network segments to contain a cyber event."),
    ("Restore from validated clean backups", "continuity", 3, ["it-systems"], "Restore systems from validated clean backups."),
    ("Switch to standalone lab/imaging mode", "continuity", 2, ["imaging", "lab"], "Run lab and imaging in standalone mode when integrations fail."),
    ("Activate manual medication-ordering process", "continuity", 2, ["pharmacy"], "Fall back to manual medication ordering during outage."),
    ("Protect critical care from IT outage impact", "continuity", 3, ["icu-beds", "it-systems"], "Prioritise critical-care continuity during systemic IT failure."),
    ("Engage cyber-incident response retainer", "continuity", 3, ["it-systems"], "Engage the contracted cyber-incident response retainer."),
    ("Preserve forensic evidence during cyber event", "continuity", 2, ["it-systems"], "Preserve forensic evidence while restoring services."),
    ("Stand up alternate communications channel", "continuity", 2, ["communication", "it-systems"], "Stand up out-of-band communications when primary channels fail."),
]


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"lever-{slug}"


def build_response_levers() -> list[dict]:
    """Build the doctrine-aligned response-lever library (advisory only)."""
    levers: list[dict] = []
    seen: set[str] = set()
    for name, category, tier, resources, description in _LEVERS:
        lever_id = _slug(name)
        if lever_id in seen:
            raise ValueError(f"duplicate leverId {lever_id}")
        seen.add(lever_id)
        levers.append(
            {
                "leverId": lever_id,
                "name": name,
                "category": category,
                "doctrineTier": tier,
                "description": description,
                "appliesToResources": resources,
                "advisoryOnly": True,
                "doctrineRef": "Swiss Lage doctrine (VKSD); ADR-0024 tier classifier",
            }
        )
    return levers


def validate_all(levers: list[dict]) -> list[str]:
    schema = load_schema("response-levers")
    errors: list[str] = []
    for lever in levers:
        errors.extend(validate(lever, schema, f"$[{lever['leverId']}]"))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the CSA response-lever library.")
    parser.add_argument("--dry-run", action="store_true", help="Validate only; never upsert.")
    args = parser.parse_args(argv)

    levers = build_response_levers()
    errors = validate_all(levers)
    if errors:
        print("FAIL: response-lever validation errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        return 1
    print(f"OK: built and validated {len(levers)} response levers.")

    if args.dry_run or not cosmos_configured():
        print("Dry run — skipping Cosmos upsert (set CSA_COSMOS_ENDPOINT to seed).")
        return 0

    count = upsert_all("response-levers", levers)
    print(f"Upserted {count} response levers into Cosmos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
