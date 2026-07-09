#!/usr/bin/env python3
"""Sprint 15 BVA synthetic FOCUS-shaped consumption generator (T1).

Emits a deterministic, daily-partitioned synthetic dataset that mirrors the
FinOps FOCUS export shape for Azure consumption, calibrated to the BVA ROM
baseline (~CHF 760k/yr Azure spend per ``docs/BVA.md`` v1.0.1). The dataset is
the "synthetic seed" for the Sprint 15 BVA Evidence data product
(``docs/superpowers/specs/2026-07-09-sprint-15-bva-design.md`` §4).

Design decisions:

* **Dependency-free core.** Row generation, FOCUS-shape validation and
  calibration use only the Python 3 standard library, so the unit tests run
  identically in CI and on a developer machine (matching the repo convention in
  ``data/synthetic/validate_datasets.py``). Parquet output is written through
  ``pyarrow`` when available; otherwise the generator falls back to
  newline-delimited JSON (``.jsonl``) or CSV. The FOCUS column shape is
  identical regardless of the output format so a future PR can swap the Bronze
  loader source with one config change.
* **Determinism.** A fixed ``--seed`` produces byte-identical output. All
  randomness flows through a single ``random.Random(seed)`` instance consumed in
  a stable iteration order.
* **Calibration.** The annual per-service cost weights sum to 1.0 and are scaled
  to the ROM baseline; per-row Gaussian noise (mean 1.0) makes plan-vs-actual
  variance realistic while keeping the annualised total within +/-15% of the
  baseline.

Example::

    python3 -m bva_synth_focus --seed 42 --days 90 --out-dir /tmp/bva

produces 90 daily partitions at
``/tmp/bva/BillingPeriod=YYYY-MM/ChargePeriodStart=YYYY-MM-DD/part-00000.<ext>``.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import os
import random
import sys
from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# Calibration constants
# --------------------------------------------------------------------------- #

# ROM baseline recurring annual Azure/platform consumption (CHF) — docs/BVA.md
# v1.0.1, "Recurring Annual Costs" table.
ROM_ANNUAL_AZURE_CHF = 760_000.0

CURRENCY = "CHF"
REGION = "switzerlandnorth"

# Tag domains (design spec §4).
HOSPITALS = ("USZ", "LUKS", "Zollikerberg", "Aggregated")
ENVIRONMENTS = ("dev", "sit", "prod")
CAPABILITIES = ("BMCA", "OOA", "DCA", "ORSA", "SBA", "CSA")


@dataclass(frozen=True)
class Service:
    """A synthetic Azure service line in the FOCUS-shaped dataset."""

    service_name: str
    service_category: str
    resource_type: str
    meter_category: str
    meter_name: str
    meter_sub_category: str
    pricing_unit: str
    # Share of the annual ROM baseline attributed to this service. Weights sum
    # to 1.0 across the catalog. Fabric, Container Apps and Cosmos are the top-3
    # by weight, matching the Sprint 14 BOM.
    weight: float


# Service catalog mirrors the Sprint 14 BOM (design spec §4). Weights sum to 1.0
# with {Fabric, Container Apps, Cosmos} as the dominant top-3 share.
SERVICES: tuple[Service, ...] = (
    Service("Microsoft Fabric", "Analytics", "Microsoft.Fabric/capacities",
            "Fabric Capacity", "F64 Capacity Unit", "Compute", "CU-hour", 0.40),
    Service("Azure Container Apps", "Compute", "Microsoft.App/containerApps",
            "Container Apps", "vCPU Active Usage", "Compute", "vCPU-second", 0.16),
    Service("Azure Cosmos DB", "Databases", "Microsoft.DocumentDB/databaseAccounts",
            "Cosmos DB", "Provisioned Throughput", "Throughput", "100 RU/s-hour", 0.13),
    Service("Azure AI Foundry", "AI + Machine Learning", "Microsoft.CognitiveServices/accounts",
            "Azure OpenAI", "Model Inference Tokens", "Inference", "1K-tokens", 0.11),
    Service("Azure Storage", "Storage", "Microsoft.Storage/storageAccounts",
            "Storage", "Hot LRS Data Stored", "Data Stored", "GB-month", 0.05),
    Service("Azure Monitor", "Management and Governance", "Microsoft.Insights/components",
            "Azure Monitor", "Metrics Ingestion", "Metrics", "10K-samples", 0.03),
    Service("Log Analytics", "Management and Governance", "Microsoft.OperationalInsights/workspaces",
            "Log Analytics", "Data Ingestion", "Analytics Logs", "GB", 0.03),
    Service("Application Insights", "Management and Governance", "Microsoft.Insights/components",
            "Application Insights", "Trace Data Ingestion", "Telemetry", "GB", 0.025),
    Service("Azure Cache for Redis", "Databases", "Microsoft.Cache/redis",
            "Cache for Redis", "C1 Standard Cache", "Cache", "hour", 0.025),
    Service("Azure Service Bus", "Integration", "Microsoft.ServiceBus/namespaces",
            "Service Bus", "Standard Operations", "Messaging", "1M-operations", 0.02),
    Service("Azure Key Vault", "Security", "Microsoft.KeyVault/vaults",
            "Key Vault", "Secrets Operations", "Operations", "10K-operations", 0.02),
)

# Ordered FOCUS columns emitted (design spec §4) plus the three tag-derived
# custom columns. Kept as the single source of truth for column order so every
# output format (parquet / jsonl / csv) is shape-identical.
FOCUS_COLUMNS: tuple[str, ...] = (
    "ChargeType", "ServiceCategory", "ServiceName", "ResourceId", "ResourceName",
    "ResourceType", "Region", "MeterName", "MeterCategory", "MeterSubCategory",
    "BillingPeriod", "ChargePeriodStart", "ChargePeriodEnd", "BilledCost",
    "EffectiveCost", "ListCost", "Quantity", "UnitPrice", "PricingUnit",
    "Currency", "x_env", "x_hospital", "x_capability",
)


def _weight_sum() -> float:
    return sum(s.weight for s in SERVICES)


def _capability_for(service_name: str, hospital: str, env: str) -> str:
    """Deterministically attribute a capability to a resource line.

    Attribution is a stable hash of the resource identity (not RNG-driven) so it
    is independent of the seed and of iteration order.
    """
    key = f"{service_name}|{hospital}|{env}"
    return CAPABILITIES[sum(ord(c) for c in key) % len(CAPABILITIES)]


def _resource_name(service: Service, hospital: str, env: str) -> str:
    slug = service.service_name.lower().replace("microsoft ", "").replace("azure ", "")
    slug = slug.replace(" for ", "-").replace(" ", "-")
    return f"{slug}-ihzhhpf-{hospital.lower()}-{env}"


def generate_rows(seed: int, days: int, end_date: _dt.date | None = None) -> list[dict]:
    """Generate the full list of FOCUS-shaped rows deterministically.

    Grain: day x service x hospital x environment. A capability tag is attributed
    to each resource line. The same ``seed`` always yields identical rows.

    Args:
        seed: RNG seed. Same seed -> identical output.
        days: number of daily partitions ending at ``end_date`` (inclusive).
        end_date: last (most recent) partition date; defaults to "yesterday"
            in UTC so the window rolls forward on nightly refresh.

    Returns:
        A list of dicts, each keyed by :data:`FOCUS_COLUMNS`.
    """
    if days <= 0:
        raise ValueError("days must be a positive integer")
    if end_date is None:
        end_date = _dt.datetime.now(_dt.timezone.utc).date() - _dt.timedelta(days=1)

    rng = random.Random(seed)
    weight_sum = _weight_sum()
    n_hospitals = len(HOSPITALS)
    n_envs = len(ENVIRONMENTS)

    rows: list[dict] = []
    start_date = end_date - _dt.timedelta(days=days - 1)
    for day_offset in range(days):
        charge_date = start_date + _dt.timedelta(days=day_offset)
        charge_start = charge_date.isoformat()
        charge_end = (charge_date + _dt.timedelta(days=1)).isoformat()
        billing_period = charge_date.strftime("%Y-%m")
        for service in SERVICES:
            annual_service_cost = ROM_ANNUAL_AZURE_CHF * (service.weight / weight_sum)
            # Baseline plan cost for one (service, hospital, env) line on one day.
            plan_line_cost = annual_service_cost / 365.0 / (n_hospitals * n_envs)
            for hospital in HOSPITALS:
                for env in ENVIRONMENTS:
                    # Gaussian noise, mean 1.0, clamped to a sane positive band
                    # so plan-vs-actual variance is realistic (design spec §4).
                    noise = rng.gauss(1.0, 0.10)
                    noise = min(1.30, max(0.70, noise))
                    effective_cost = round(plan_line_cost * noise, 4)
                    # List price is ~8% above effective (negotiated discount);
                    # billed equals effective in this synthetic model.
                    list_cost = round(effective_cost * 1.08, 4)
                    unit_price = round(rng.uniform(0.05, 5.0), 4)
                    quantity = round(effective_cost / unit_price, 4) if unit_price else 0.0
                    resource_name = _resource_name(service, hospital, env)
                    rows.append({
                        "ChargeType": "Usage",
                        "ServiceCategory": service.service_category,
                        "ServiceName": service.service_name,
                        "ResourceId": (
                            f"/subscriptions/00000000-0000-0000-0000-000000000000"
                            f"/resourceGroups/rg-ihzhhpf-{env}"
                            f"/providers/{service.resource_type}/{resource_name}"
                        ),
                        "ResourceName": resource_name,
                        "ResourceType": service.resource_type,
                        "Region": REGION,
                        "MeterName": service.meter_name,
                        "MeterCategory": service.meter_category,
                        "MeterSubCategory": service.meter_sub_category,
                        "BillingPeriod": billing_period,
                        "ChargePeriodStart": charge_start,
                        "ChargePeriodEnd": charge_end,
                        "BilledCost": effective_cost,
                        "EffectiveCost": effective_cost,
                        "ListCost": list_cost,
                        "Quantity": quantity,
                        "UnitPrice": unit_price,
                        "PricingUnit": service.pricing_unit,
                        "Currency": CURRENCY,
                        "x_env": env,
                        "x_hospital": hospital,
                        "x_capability": _capability_for(service.service_name, hospital, env),
                    })
    return rows


def annualized_total(rows: list[dict], days: int) -> float:
    """Annualise the ``EffectiveCost`` sum over a ``days``-long window."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    total = sum(float(r["EffectiveCost"]) for r in rows)
    return total * 365.0 / days


def service_cost_shares(rows: list[dict]) -> dict[str, float]:
    """Return the fractional cost share per ``ServiceName`` (sums to ~1.0)."""
    totals: dict[str, float] = {}
    for row in rows:
        totals[row["ServiceName"]] = totals.get(row["ServiceName"], 0.0) + float(row["EffectiveCost"])
    grand = sum(totals.values()) or 1.0
    return {name: value / grand for name, value in totals.items()}


# --------------------------------------------------------------------------- #
# FOCUS-shape validation (dependency-free)
# --------------------------------------------------------------------------- #

def load_focus_schema(path: str | None = None) -> dict:
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "tests", "fixtures", "focus_schema.json",
        )
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_month(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        _dt.datetime.strptime(value, "%Y-%m")
        return True
    except ValueError:
        return False


def _is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        _dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_focus_shape(rows: list[dict], schema: dict) -> list[str]:
    """Validate rows against the FOCUS column contract; return error strings.

    An empty list means the dataset conforms to the shape.
    """
    errors: list[str] = []
    columns = schema.get("columns", [])
    expected_names = [c["name"] for c in columns]
    if not rows:
        errors.append("dataset is empty")
        return errors
    for index, row in enumerate(rows):
        extra = set(row) - set(expected_names)
        if extra:
            errors.append(f"row {index}: unexpected columns {sorted(extra)}")
        for column in columns:
            name = column["name"]
            if name not in row:
                errors.append(f"row {index}: missing column '{name}'")
                continue
            value = row[name]
            col_type = column.get("type")
            # Diagnostics deliberately report the column name and the offending
            # value's *type* only — never the raw value — so validating an
            # untrusted dataset cannot echo its contents into logs.
            if col_type == "string" and not isinstance(value, str):
                errors.append(f"row {index}: '{name}' expected string, got {type(value).__name__}")
            elif col_type == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
                errors.append(f"row {index}: '{name}' expected number, got {type(value).__name__}")
            elif col_type == "date" and not _is_date(value):
                errors.append(f"row {index}: '{name}' expected date (YYYY-MM-DD), got {type(value).__name__}")
            elif col_type == "month" and not _is_month(value):
                errors.append(f"row {index}: '{name}' expected month (YYYY-MM), got {type(value).__name__}")
            enum = column.get("enum")
            if enum is not None and value not in enum:
                errors.append(f"row {index}: '{name}' value not in enum {enum}")
    return errors


# --------------------------------------------------------------------------- #
# Output writers
# --------------------------------------------------------------------------- #

def _partition_dir(out_dir: str, billing_period: str, charge_start: str) -> str:
    return os.path.join(
        out_dir,
        f"BillingPeriod={billing_period}",
        f"ChargePeriodStart={charge_start}",
    )


def _rows_by_partition(rows: list[dict]) -> "dict[tuple[str, str], list[dict]]":
    partitions: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (row["BillingPeriod"], row["ChargePeriodStart"])
        partitions.setdefault(key, []).append(row)
    return partitions


def _serialize_jsonl(rows: list[dict]) -> str:
    ordered = [
        {col: row[col] for col in FOCUS_COLUMNS}
        for row in rows
    ]
    return "".join(json.dumps(r, sort_keys=False, separators=(",", ":")) + "\n" for r in ordered)


def _serialize_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(FOCUS_COLUMNS), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row[col] for col in FOCUS_COLUMNS})
    return buffer.getvalue()


def _write_parquet(rows: list[dict], path: str) -> None:
    # Guarded optional-dependency import: pyarrow is only needed for Parquet
    # output; the generator falls back to jsonl/csv when it is absent.
    import pyarrow as pa
    import pyarrow.parquet as pq

    columns = {col: [row[col] for row in rows] for col in FOCUS_COLUMNS}
    table = pa.table(columns)
    pq.write_table(table, path)


def _resolve_format(fmt: str) -> str:
    if fmt != "auto":
        return fmt
    try:
        # Guarded optional-dependency probe: prefer Parquet only when pyarrow
        # is installed, otherwise fall back to jsonl.
        import pyarrow  # noqa: F401
        return "parquet"
    except ImportError:
        return "jsonl"


def write_partitioned(rows: list[dict], out_dir: str, fmt: str = "auto") -> list[str]:
    """Write rows to daily partitions and return the list of file paths written."""
    resolved = _resolve_format(fmt)
    ext = {"parquet": "parquet", "jsonl": "jsonl", "csv": "csv"}[resolved]
    written: list[str] = []
    for (billing_period, charge_start), part_rows in sorted(_rows_by_partition(rows).items()):
        directory = _partition_dir(out_dir, billing_period, charge_start)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"part-00000.{ext}")
        if resolved == "parquet":
            _write_parquet(part_rows, path)
        else:
            payload = _serialize_jsonl(part_rows) if resolved == "jsonl" else _serialize_csv(part_rows)
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(payload)
        written.append(path)
    return written


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _parse_args(argv: "list[str] | None") -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bva_synth_focus",
        description="Generate a deterministic FOCUS-shaped synthetic Azure "
                    "consumption seed for the Sprint 15 BVA data product.",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default: 42).")
    parser.add_argument("--days", type=int, default=90,
                        help="Number of daily partitions to generate (default: 90).")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="Output directory. If omitted, prints a summary only.")
    parser.add_argument("--format", choices=("auto", "parquet", "jsonl", "csv"),
                        default="auto",
                        help="Output format. 'auto' uses parquet when pyarrow is "
                             "available, otherwise jsonl (default: auto).")
    parser.add_argument("--end-date", type=str, default=None,
                        help="Last partition date (YYYY-MM-DD). Defaults to yesterday (UTC).")
    return parser.parse_args(argv)


def main(argv: "list[str] | None" = None) -> int:
    args = _parse_args(argv)
    end_date = _dt.date.fromisoformat(args.end_date) if args.end_date else None
    rows = generate_rows(seed=args.seed, days=args.days, end_date=end_date)

    schema = load_focus_schema()
    shape_errors = validate_focus_shape(rows, schema)
    if shape_errors:
        for error in shape_errors[:20]:
            print(f"FOCUS-shape error: {error}", file=sys.stderr)
        print(f"FOCUS-shape validation failed with {len(shape_errors)} error(s).",
              file=sys.stderr)
        return 1

    annual = annualized_total(rows, args.days)
    lower, upper = ROM_ANNUAL_AZURE_CHF * 0.85, ROM_ANNUAL_AZURE_CHF * 1.15
    calibrated = lower <= annual <= upper

    if args.out_dir:
        written = write_partitioned(rows, args.out_dir, args.format)
        print(f"Wrote {len(written)} daily partition(s) to {args.out_dir} "
              f"({_resolve_format(args.format)}).")
    else:
        print("Dry run (no --out-dir): dataset generated in memory only.")

    print(f"Rows: {len(rows)} | Partitions: {args.days} | "
          f"Annualised total: CHF {annual:,.0f} "
          f"(baseline CHF {ROM_ANNUAL_AZURE_CHF:,.0f}, "
          f"{'within' if calibrated else 'OUTSIDE'} +/-15%).")

    return 0 if calibrated else 2


if __name__ == "__main__":
    raise SystemExit(main())
