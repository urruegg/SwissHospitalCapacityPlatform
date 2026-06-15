# Notebook: nb_silver_transform
# Walking-skeleton: bronze.episode -> silver.episode (+ silver.episode_quarantine)
# Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
# Implements: FR-DATA-001 (Episode as control unit), FR-DATA-003 (pseudonymisation invariant)
# Lakehouse: lh_chhealthpf_sit

# COMMAND ----------

from _lib import transforms

# COMMAND ----------

LAKEHOUSE = "lh_chhealthpf_sit"
BRONZE_TABLE = f"{LAKEHOUSE}.bronze_episode"
SILVER_TABLE = f"{LAKEHOUSE}.silver_episode"
QUARANTINE_TABLE = f"{LAKEHOUSE}.silver_episode_quarantine"

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
