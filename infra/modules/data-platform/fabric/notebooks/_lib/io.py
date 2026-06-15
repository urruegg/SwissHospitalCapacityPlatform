"""Delta MERGE upsert helper. Separate from `transforms.py` to keep transforms pure."""
from __future__ import annotations

from typing import Sequence

from pyspark.sql import DataFrame, SparkSession


def merge_upsert(
    spark: SparkSession,
    source: DataFrame,
    target_table: str,
    key_cols: Sequence[str],
) -> None:
    """Idempotent upsert via Delta MERGE INTO on `key_cols` (spec sec.6.3).

    Creates `target_table` if absent (schema = source schema, zero rows), then runs
    MERGE INTO ... ON <key_cols> WHEN MATCHED UPDATE * WHEN NOT MATCHED INSERT *.
    """
    if not key_cols:
        raise ValueError("merge_upsert requires at least one key column")

    source.limit(0).write.format("delta").mode("ignore").saveAsTable(target_table)

    temp_view = f"_merge_src_{abs(hash(target_table))}"
    source.createOrReplaceTempView(temp_view)
    try:
        on_clause = " AND ".join(f"t.{c} = s.{c}" for c in key_cols)
        spark.sql(
            f"""
            MERGE INTO {target_table} t
            USING {temp_view} s
            ON {on_clause}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            """
        )
    finally:
        spark.catalog.dropTempView(temp_view)
