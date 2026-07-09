"""Pure transform rules for the Sprint 15 BVA medallion (T3).

Framework-agnostic (no PySpark / no I/O) implementation of the Bronze → Silver →
Gold transforms for the BVA Evidence data product. The Fabric notebooks in this
folder read the Delta / Files sources, ``collect()`` the (synthetic, ~12k-row)
rows to plain dicts, apply these functions, and write the Gold star schema back
as Delta. Keeping the logic here makes it unit-testable with a byte-stable
golden fixture — the same convention as
``data-platform/notebooks/evidence/readiness_rules.py``.

Gold star schema (design spec §5, snake_case + ``gold.`` prefix per PR #153):

* Facts: ``gold.bva_fact_azure_consumption`` (resource × meter × day),
  ``gold.bva_fact_budget`` (env × capability × month, plan baseline),
  ``gold.bva_fact_value_realization`` (capability × month × hospital; adoption joined
  in T4).
* Dims: ``gold.bva_dim_service``, ``gold.bva_dim_meter``, ``gold.bva_dim_resource``,
  ``gold.bva_dim_environment``, ``gold.bva_dim_hospital``, ``gold.bva_dim_capability``,
  ``gold.bva_dim_date``, ``gold.bva_dim_exec_role``.

All aggregation output is returned **sorted** so JSON serialisation is
byte-stable across runs for a fixed input (regression-testable).
"""
from __future__ import annotations

from typing import Iterable, Mapping

# --------------------------------------------------------------------------- #
# Synthetic value-realization calibration (design spec §5–§6).
#
# These are *synthetic* rates used to derive plan-vs-actual value KPIs from the
# FOCUS consumption seed. They are deliberately simple and documented so the
# derived KPIs stay explainable in a board setting. No PHI, no real financials.
# --------------------------------------------------------------------------- #

# Benefit realized per capability, expressed as a value-to-cost multiplier on the
# allocated Azure consumption. Grounded to the ROM BVA case (net benefit >> cost).
BENEFIT_MULTIPLIER: dict[str, float] = {
    "BMCA": 6.0,
    "OOA": 5.0,
    "DCA": 7.0,
    "ORSA": 4.5,
    "SBA": 4.0,
    "CSA": 3.5,
}
_DEFAULT_BENEFIT_MULTIPLIER = 4.0

# Decision cycles per CHF 1000 of allocated capability cost (synthetic, stable).
DECISION_CYCLES_PER_KCHF: dict[str, float] = {
    "BMCA": 120.0,
    "OOA": 90.0,
    "DCA": 80.0,
    "ORSA": 60.0,
    "SBA": 70.0,
    "CSA": 40.0,
}
_DEFAULT_DECISION_CYCLES = 75.0

EXEC_ROLES: tuple[tuple[str, str], ...] = (
    ("CEO", "Chief Executive Officer"),
    ("CFO", "Chief Financial Officer"),
    ("CIO", "Chief Information Officer"),
    ("COO", "Chief Operating Officer"),
    ("CTO", "Chief Technology Officer"),
    ("BOARD", "Board (shared summary)"),
)

# Map an Entra app role (persona ``app_role``) to the capability whose adoption
# it drives (design spec §4 capabilities). Governance / admin / read-only roles
# are intentionally unmapped — they do not count toward capability adoption.
DEFAULT_ROLE_CAPABILITY: dict[str, str] = {
    "HCC.BedManager": "BMCA",
    "HCC.FlowManager": "OOA",
    "HCC.OperationsLead": "OOA",
    "HCC.EDLead": "OOA",
    "HCC.DischargeCoordinator": "DCA",
    "HCC.ORCoordinator": "ORSA",
    "HCC.StaffingCoordinator": "SBA",
    "HCC.CrisisManager": "CSA",
}

# A successful Entra sign-in has resultType "0".
_SIGNIN_SUCCESS = "0"


def _num(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------------- #
# Silver
# --------------------------------------------------------------------------- #

def to_silver(
    focus_rows: Iterable[Mapping],
    *,
    ingest_utc: str,
    source_seed: int,
) -> list[dict]:
    """Normalise Bronze FOCUS rows into Silver with keys + provenance.

    Adds foreign keys (``*_key``), a ``date_key`` / ``month_key`` and the
    provenance columns ``_ingest_utc`` / ``_source_seed`` (design spec §5). The
    FOCUS measure columns are preserved. Output is sorted for byte-stability.
    """
    out: list[dict] = []
    for row in focus_rows:
        out.append(
            {
                "date_key": row["ChargePeriodStart"],
                "month_key": row["BillingPeriod"],
                "service_key": row["ServiceName"],
                "meter_key": row["MeterName"],
                "resource_key": row["ResourceId"],
                "env_key": row["x_env"],
                "hospital_key": row["x_hospital"],
                "capability_key": row["x_capability"],
                "effective_cost": _num(row.get("EffectiveCost")),
                "billed_cost": _num(row.get("BilledCost")),
                "list_cost": _num(row.get("ListCost")),
                "quantity": _num(row.get("Quantity")),
                "currency": row.get("Currency", "CHF"),
                "_ingest_utc": ingest_utc,
                "_source_seed": int(source_seed),
            }
        )
    out.sort(key=lambda r: (r["date_key"], r["resource_key"], r["meter_key"]))
    return out


# --------------------------------------------------------------------------- #
# Gold dimensions
# --------------------------------------------------------------------------- #

def dim_service(focus_rows: Iterable[Mapping]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in focus_rows:
        key = row["ServiceName"]
        seen.setdefault(
            key,
            {
                "service_key": key,
                "service_name": key,
                "service_category": row["ServiceCategory"],
            },
        )
    return [seen[k] for k in sorted(seen)]


def dim_meter(focus_rows: Iterable[Mapping]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in focus_rows:
        key = row["MeterName"]
        seen.setdefault(
            key,
            {
                "meter_key": key,
                "meter_name": key,
                "meter_category": row["MeterCategory"],
                "meter_sub_category": row["MeterSubCategory"],
                "pricing_unit": row["PricingUnit"],
            },
        )
    return [seen[k] for k in sorted(seen)]


def dim_resource(focus_rows: Iterable[Mapping]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in focus_rows:
        key = row["ResourceId"]
        seen.setdefault(
            key,
            {
                "resource_key": key,
                "resource_name": row["ResourceName"],
                "resource_type": row["ResourceType"],
                "region": row["Region"],
                "service_key": row["ServiceName"],
                "env_key": row["x_env"],
                "hospital_key": row["x_hospital"],
                "capability_key": row["x_capability"],
            },
        )
    return [seen[k] for k in sorted(seen)]


def _distinct_dim(focus_rows: Iterable[Mapping], column: str, key_name: str) -> list[dict]:
    values = sorted({row[column] for row in focus_rows})
    return [{key_name: v} for v in values]


def dim_environment(focus_rows: Iterable[Mapping]) -> list[dict]:
    return _distinct_dim(focus_rows, "x_env", "env_key")


def dim_hospital(focus_rows: Iterable[Mapping]) -> list[dict]:
    return _distinct_dim(focus_rows, "x_hospital", "hospital_key")


def dim_capability(focus_rows: Iterable[Mapping]) -> list[dict]:
    return _distinct_dim(focus_rows, "x_capability", "capability_key")


def dim_date(focus_rows: Iterable[Mapping]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in focus_rows:
        key = row["ChargePeriodStart"]
        if key in seen:
            continue
        year, month, day = (int(p) for p in key.split("-"))
        seen[key] = {
            "date_key": key,
            "month_key": row["BillingPeriod"],
            "year": year,
            "month": month,
            "day": day,
        }
    return [seen[k] for k in sorted(seen)]


def dim_exec_role() -> list[dict]:
    return [{"exec_role_key": key, "exec_role_name": name} for key, name in EXEC_ROLES]


# --------------------------------------------------------------------------- #
# Gold facts
# --------------------------------------------------------------------------- #

def _round_costs(row: dict) -> dict:
    row["effective_cost"] = round(row["effective_cost"], 2)
    row["billed_cost"] = round(row["billed_cost"], 2)
    row["list_cost"] = round(row["list_cost"], 2)
    row["quantity"] = round(row["quantity"], 4)
    return row


def fact_azure_consumption(silver_rows: Iterable[Mapping]) -> list[dict]:
    """Aggregate Silver to resource × meter × day (design spec §5)."""
    groups: dict[tuple, dict] = {}
    for row in silver_rows:
        gk = (
            row["resource_key"],
            row["meter_key"],
            row["date_key"],
            row["env_key"],
            row["hospital_key"],
            row["capability_key"],
        )
        agg = groups.setdefault(
            gk,
            {
                "resource_key": gk[0],
                "meter_key": gk[1],
                "date_key": gk[2],
                "env_key": gk[3],
                "hospital_key": gk[4],
                "capability_key": gk[5],
                "effective_cost": 0.0,
                "billed_cost": 0.0,
                "list_cost": 0.0,
                "quantity": 0.0,
            },
        )
        agg["effective_cost"] += _num(row.get("effective_cost"))
        agg["billed_cost"] += _num(row.get("billed_cost"))
        agg["list_cost"] += _num(row.get("list_cost"))
        agg["quantity"] += _num(row.get("quantity"))
    out = [_round_costs(v) for v in groups.values()]
    out.sort(key=lambda r: (r["date_key"], r["resource_key"], r["meter_key"]))
    return out


def fact_budget(silver_rows: Iterable[Mapping]) -> list[dict]:
    """Plan baseline per env × capability × month (design spec §5).

    The plan is the **mean monthly actual** across the window for each
    (env, capability), giving each month a stable target so plan-vs-actual
    variance is realistic and non-trivial.
    """
    monthly: dict[tuple, float] = {}
    for row in silver_rows:
        gk = (row["env_key"], row["capability_key"], row["month_key"])
        monthly[gk] = monthly.get(gk, 0.0) + _num(row.get("effective_cost"))

    # Mean monthly actual per (env, capability).
    by_ec: dict[tuple, list[float]] = {}
    for (env, cap, _month), total in monthly.items():
        by_ec.setdefault((env, cap), []).append(total)
    plan_baseline = {ec: (sum(values) / len(values)) for ec, values in by_ec.items()}

    out = []
    for (env, cap, month), actual in monthly.items():
        plan = plan_baseline[(env, cap)]
        out.append(
            {
                "env_key": env,
                "capability_key": cap,
                "month_key": month,
                "plan_cost": round(plan, 2),
                "actual_cost": round(actual, 2),
                "variance_cost": round(actual - plan, 2),
            }
        )
    out.sort(key=lambda r: (r["month_key"], r["env_key"], r["capability_key"]))
    return out


def fact_value_realization(
    silver_rows: Iterable[Mapping],
    adoption_index: Mapping[tuple, int] | None = None,
) -> list[dict]:
    """Value realization per capability × month × hospital (design spec §5).

    ``adoption_index`` maps ``(capability_key, month_key, hospital_key) -> active
    user count``. When absent (T3 — before the Sprint 12 join in T4) the adoption
    count is ``0`` and ``benefit_realized`` is derived from the allocated cost and
    the synthetic :data:`BENEFIT_MULTIPLIER` alone. T4 supplies the index.
    """
    groups: dict[tuple, dict] = {}
    for row in silver_rows:
        gk = (row["capability_key"], row["month_key"], row["hospital_key"])
        agg = groups.setdefault(
            gk,
            {
                "capability_key": gk[0],
                "month_key": gk[1],
                "hospital_key": gk[2],
                "allocated_cost": 0.0,
            },
        )
        agg["allocated_cost"] += _num(row.get("effective_cost"))

    out = []
    for gk, agg in groups.items():
        cap = agg["capability_key"]
        allocated = agg["allocated_cost"]
        multiplier = BENEFIT_MULTIPLIER.get(cap, _DEFAULT_BENEFIT_MULTIPLIER)
        cycles_rate = DECISION_CYCLES_PER_KCHF.get(cap, _DEFAULT_DECISION_CYCLES)
        adoption = int(adoption_index.get(gk, 0)) if adoption_index else 0
        out.append(
            {
                "capability_key": cap,
                "month_key": agg["month_key"],
                "hospital_key": agg["hospital_key"],
                "allocated_cost": round(allocated, 2),
                "benefit_realized": round(allocated * multiplier, 2),
                "adoption_count": adoption,
                "decision_cycles": round(allocated / 1000.0 * cycles_rate, 1),
            }
        )
    out.sort(key=lambda r: (r["month_key"], r["capability_key"], r["hospital_key"]))
    return out


# --------------------------------------------------------------------------- #
# Adoption telemetry join (T4)
# --------------------------------------------------------------------------- #

def adoption_index_from_signins(
    signins: Iterable[Mapping],
    persona_hospital: Mapping[str, str] | None = None,
    role_capability: Mapping[str, str] | None = None,
) -> dict[tuple, int]:
    """Build the ``(capability, month, hospital) -> distinct active users`` index.

    Sprint 15 · T4. Consumes Sprint 12 sign-in rows (Bronze ``bva_adoption`` — or
    the 30-day synthetic backfill from ``adoption_seed_synthetic.py`` per design
    spec §14) and produces the adoption index consumed by
    :func:`fact_value_realization`.

    * Only **successful** sign-ins (``resultType == "0"``) count.
    * ``appRole`` is mapped to a capability via ``role_capability``
      (default :data:`DEFAULT_ROLE_CAPABILITY`); unmapped governance/admin roles
      are skipped.
    * The user's hospital comes from ``persona_hospital[upn]`` (built from
      ``personas.csv``); an unknown user falls back to ``Aggregated``.
    * The month comes from the ``YYYY-MM`` prefix of ``signInTimestamp``.
    * The value is the count of **distinct** ``upn`` in each group (active users).
    """
    role_map = role_capability or DEFAULT_ROLE_CAPABILITY
    hospitals = persona_hospital or {}

    groups: dict[tuple, set] = {}
    for row in signins:
        if str(row.get("resultType")) != _SIGNIN_SUCCESS:
            continue
        capability = role_map.get(row.get("appRole"))
        if not capability:
            continue
        timestamp = str(row.get("signInTimestamp", ""))
        if len(timestamp) < 7:
            continue
        month = timestamp[:7]
        upn = row.get("upn")
        if not upn:
            continue
        hospital = hospitals.get(upn, "Aggregated")
        groups.setdefault((capability, month, hospital), set()).add(upn)

    return {gk: len(users) for gk, users in groups.items()}

