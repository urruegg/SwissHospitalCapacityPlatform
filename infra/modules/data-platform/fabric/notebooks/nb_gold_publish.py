# Notebook: nb_gold_publish
# Walking-skeleton: silver.episode -> gold.demand_encounter (DC envelope assertion)
# Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
# Implements: FR-DATA-005 (capacity demand as DC), NFR-GOV-006 (purpose tags + residency envelope)
# Lakehouse: lh_ihzhhpf_sit

# COMMAND ----------

from pyspark.sql import functions as F

from _lib import io, transforms

# COMMAND ----------

LAKEHOUSE = "lh_ihzhhpf_sit"
SILVER_TABLE = f"{LAKEHOUSE}.silver.episode"
BRONZE_EVENTS_TABLE = f"{LAKEHOUSE}.bronze.events_demand_encounter"
GOLD_TABLE = f"{LAKEHOUSE}.gold.demand_encounter"
PROVENANCE_SOURCE = "kis-mirror"

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {LAKEHOUSE}.gold")

# COMMAND ----------

silver = spark.read.format("delta").table(SILVER_TABLE)

# COMMAND ----------

gold = transforms.silver_episode_to_gold_demand_encounter(
    silver,
    provenance_source=PROVENANCE_SOURCE,
)

# COMMAND ----------

# Idempotent MERGE on episode_id (natural key) per spec sec.6.3.
io.merge_upsert(spark, gold, GOLD_TABLE, key_cols=["episode_id"])

# COMMAND ----------

# Optional W1.5 streaming path: merge simulator events when bronze table exists.
if spark.catalog.tableExists(BRONZE_EVENTS_TABLE):
    bronze_events = spark.read.format("delta").table(BRONZE_EVENTS_TABLE)

    if "records" in bronze_events.columns:
        simulator_records = bronze_events.select(F.explode("records").alias("r")).select("r.*")
    else:
        simulator_records = bronze_events

    required_fields = [
        "encounterId",
        "pseudonymId",
        "expectedArrivalTimestamp",
        "expectedLOSDays",
        "requestedSpecialtyServiceId",
        "asOfTimestamp",
    ]
    missing = [c for c in required_fields if c not in simulator_records.columns]
    if missing:
        raise ValueError(f"Simulator bronze events missing required fields: {missing}")

    simulator_gold = transforms.simulator_records_to_gold_demand_encounter(simulator_records)
    io.merge_upsert(spark, simulator_gold, GOLD_TABLE, key_cols=["episode_id"])
