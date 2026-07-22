"""Sprint 21 M9 — Gold forecast overlay for Trusted External Signals.

Pure functions build deterministic adjustment rows and an adjusted forecast view
without Spark. The Fabric entrypoint wraps them to write Gold Delta tables.
"""
from __future__ import annotations

import sys
from typing import Dict, List

try:
    import forecast_uplift as fu
except ModuleNotFoundError:  # pragma: no cover - Fabric notebook resource path
    sys.path.insert(0, "builtin/external-signals")
    import forecast_uplift as fu

_ELIGIBLE_STATUS = {"Actual"}
_ELIGIBLE_TRUST = {"A"}
WARD_SPECIALTY_TABLE = "gold.dim_ward_capacityunit"

_ADJUSTMENT_COLUMNS = [
    "signalId", "hazardType", "severity", "hospital", "ward_id", "specialty_id",
    "canton", "date", "effective", "onset", "expires", "upliftFactor", "baseRequiredCapacity",
    "adjustedRequiredCapacity", "rationale", "rawHash", "connectorVersion", "ingestedAt", "licence",
]
_VIEW_COLUMNS = ["hospital", "ward_id", "date", "baseRequiredCapacity", "adjustedRequiredCapacity", "attribution"]


def _eligible(signal: dict) -> bool:
    return signal.get("status") in _ELIGIBLE_STATUS and signal.get("trustTier") in _ELIGIBLE_TRUST


def _signal_key(signal: dict) -> tuple:
    if signal.get("signalId"):
        return ("signalId", signal.get("signalId"))
    cantons = tuple(sorted((signal.get("region") or {}).get("cantons", [])))
    return (
        "derived",
        signal.get("sourceId"),
        signal.get("capIdentifier"),
        signal.get("hazardType"),
        cantons,
        signal.get("onset"),
    )


def dedupe_signals(signals: List[dict]) -> List[dict]:
    """Collapse re-published eligible signal rows before multiplicative uplift."""
    latest: Dict[tuple, dict] = {}
    for signal in signals:
        key = _signal_key(signal)
        current = latest.get(key)
        ingested = (signal.get("provenance") or {}).get("ingestedAt") or ""
        current_ingested = ((current or {}).get("provenance") or {}).get("ingestedAt") or ""
        if current is None or ingested >= current_ingested:
            latest[key] = signal
    return [latest[key] for key in sorted(latest)]


def build_adjustment_rows(
    base_forecast: List[dict],
    signals: List[dict],
    ward_specialty: Dict[str, str],
    hospital_canton: Dict[str, str],
    uplift_map: dict,
) -> List[dict]:
    """Build one audit row per eligible signal and affected forecast bucket."""
    clamp = uplift_map.get("clamp", 2.0)
    rows: List[dict] = []
    for sig in dedupe_signals([signal for signal in signals if _eligible(signal)]):
        cantons = set((sig.get("region") or {}).get("cantons", []))
        for fc in base_forecast:
            hospital = fc["hospital"]
            ward_id = fc["ward_id"]
            canton = hospital_canton.get(hospital)
            if canton not in cantons:
                continue
            if not fu.signal_applies(fc["date"], sig.get("onset"), sig.get("expires")):
                continue
            specialty = ward_specialty.get(ward_id)
            factor = fu.uplift_factor(sig.get("hazardType"), sig.get("severity"), specialty, uplift_map)
            if factor <= 0.0:
                continue
            base = float(fc["required_capacity"])
            prov = sig.get("provenance") or {}
            rows.append({
                "signalId": sig["signalId"],
                "hazardType": sig.get("hazardType"),
                "severity": sig.get("severity"),
                "hospital": hospital,
                "ward_id": ward_id,
                "specialty_id": specialty,
                "canton": canton,
                "date": fc["date"],
                "effective": sig.get("effective"),
                "onset": sig.get("onset"),
                "expires": sig.get("expires"),
                "upliftFactor": factor,
                "baseRequiredCapacity": base,
                "adjustedRequiredCapacity": fu.combine(base, [factor], clamp),
                "rationale": (
                    f"{sig.get('hazardType')}/{sig.get('severity')} signal {sig['signalId']} "
                    f"over {canton} lifts {specialty} demand +{int(round(factor * 100))}%"
                ),
                "rawHash": prov.get("rawHash"),
                "connectorVersion": prov.get("connectorVersion"),
                "ingestedAt": prov.get("ingestedAt"),
                "licence": prov.get("licence"),
            })
    return rows


def build_adjusted_view(base_forecast: List[dict], adjustment_rows: List[dict], clamp: float = 2.0) -> List[dict]:
    """Build one adjusted view row per base forecast bucket with attribution."""
    by_key: Dict[tuple, List[dict]] = {}
    for adj in adjustment_rows:
        by_key.setdefault((adj["hospital"], adj["ward_id"], adj["date"]), []).append(adj)

    out: List[dict] = []
    for fc in base_forecast:
        key = (fc["hospital"], fc["ward_id"], fc["date"])
        adjs = by_key.get(key, [])
        base = float(fc["required_capacity"])
        out.append({
            "hospital": fc["hospital"],
            "ward_id": fc["ward_id"],
            "date": fc["date"],
            "baseRequiredCapacity": base,
            "adjustedRequiredCapacity": fu.combine(base, [a["upliftFactor"] for a in adjs], clamp),
            "attribution": [a["signalId"] for a in adjs],
        })
    return out


def _schema(schema_kind: str):  # pragma: no cover - depends on pyspark
    from pyspark.sql.types import ArrayType, DoubleType, StringType, StructField, StructType

    string_cols = {
        "signalId", "hazardType", "severity", "hospital", "ward_id", "specialty_id",
        "canton", "date", "effective", "onset", "expires", "rationale", "rawHash",
        "connectorVersion", "ingestedAt", "licence",
    }
    double_cols = {"upliftFactor", "baseRequiredCapacity", "adjustedRequiredCapacity"}
    fields = []
    columns = _ADJUSTMENT_COLUMNS if schema_kind == "adjustment" else _VIEW_COLUMNS
    for col in columns:
        if col == "attribution":
            data_type = ArrayType(StringType())
        elif col in double_cols:
            data_type = DoubleType()
        elif col in string_cols:
            data_type = StringType()
        else:
            data_type = StringType()
        fields.append(StructField(col, data_type, True))
    return StructType(fields)


def _write_rows(spark, rows: List[dict], columns: List[str], table_name: str, schema_kind: str) -> None:  # pragma: no cover
    from pyspark.sql import Row

    ordered = [{col: row.get(col) for col in columns} for row in rows]
    data = [Row(**row) for row in ordered]
    if data:
        frame = spark.createDataFrame(data)
    else:
        frame = spark.createDataFrame([], _schema(schema_kind))
    frame \
        .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table_name)


def write_gold_tables(spark, adj_rows: List[dict], view_rows: List[dict], writer=_write_rows) -> None:
    writer(
        spark,
        adj_rows,
        _ADJUSTMENT_COLUMNS,
        "gold.ext_fact_forecast_adjustment",
        "adjustment",
    )
    writer(
        spark,
        [{**row, "attribution": list(row["attribution"])} for row in view_rows],
        _VIEW_COLUMNS,
        "gold.vw_forecast_adjusted",
        "view",
    )


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    from pyspark.sql import SparkSession, functions as F

    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")

    base = [r.asDict() for r in spark.table("gold.forecast_output")
            .select("hospital", "ward_id", F.col("date").cast("string").alias("date"),
                    F.col("required_capacity").cast("double").alias("required_capacity"))
            .collect()]
    signals = [r.asDict(recursive=True) for r in spark.table("silver.ext_signal")
               .where("status = 'Actual' AND trustTier = 'A'")
               .collect()]
    ward_specialty = {r["ward_id"]: r["specialty_id"] for r in spark.table(WARD_SPECIALTY_TABLE)
                      .select("ward_id", "specialty_id").collect()}
    hospital_canton = {r["hospital_id"]: r["canton"] for r in spark.table("gold.dim_hospital")
                       .select("hospital_id", "canton").collect()}

    uplift_map = fu.load_uplift_map()
    adj_rows = build_adjustment_rows(base, signals, ward_specialty, hospital_canton, uplift_map)
    view_rows = build_adjusted_view(base, adj_rows, uplift_map.get("clamp", 2.0))

    write_gold_tables(spark, adj_rows, view_rows)
    print(f"adjustment rows: {len(adj_rows)}; view rows: {len(view_rows)}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
