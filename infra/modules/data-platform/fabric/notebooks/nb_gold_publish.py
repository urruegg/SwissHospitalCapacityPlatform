# Notebook: nb_gold_publish
# Walking-skeleton: silver.episode -> gold.demand_encounter (DC envelope assertion)
# Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
# Implements: FR-DATA-005 (capacity demand as DC), NFR-GOV-006 (purpose tags + residency envelope)
# Lakehouse: lh_chhealthpf_sit

# COMMAND ----------

from _lib import transforms

# COMMAND ----------

LAKEHOUSE = "lh_chhealthpf_sit"
SILVER_TABLE = f"{LAKEHOUSE}.silver_episode"
GOLD_TABLE = f"{LAKEHOUSE}.gold_demand_encounter"
PROVENANCE_SOURCE = "kis-mirror"

# COMMAND ----------

silver = spark.read.format("delta").table(SILVER_TABLE)

# COMMAND ----------

gold = transforms.silver_episode_to_gold_demand_encounter(
    silver,
    provenance_source=PROVENANCE_SOURCE,
)

# COMMAND ----------

(
    gold.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_TABLE)
)
