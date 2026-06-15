# Notebook: nb_silver_transform
# Walking-skeleton: kis.Episode (mirror landing) -> silver.episode (+ silver.quarantine_episode)
# Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
# Implements: FR-DATA-001 (Episode as control unit), FR-DATA-003 (pseudonymisation invariant)
# Lakehouse: lh_chhealthpf_sit (enableSchemas=true; mirror lands source dbo schema as `kis`).
# Spec uses `bronze.kis_*` naming; the W1.2 mirror lands at `kis.Episode` — this notebook
# bridges that gap for the walking skeleton (no separate bronze rename layer yet).

# COMMAND ----------

from _lib import transforms

# COMMAND ----------

LAKEHOUSE = "lh_chhealthpf_sit"
BRONZE_TABLE = f"{LAKEHOUSE}.kis.Episode"
SILVER_TABLE = f"{LAKEHOUSE}.silver.episode"
QUARANTINE_TABLE = f"{LAKEHOUSE}.silver.quarantine_episode"

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {LAKEHOUSE}.silver")

# COMMAND ----------

bronze = spark.read.format("delta").table(BRONZE_TABLE)

# COMMAND ----------

silver, quarantine = transforms.bronze_to_silver_episode_with_quarantine(bronze)

# COMMAND ----------

(
    silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)

# COMMAND ----------

(
    quarantine.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(QUARANTINE_TABLE)
)
