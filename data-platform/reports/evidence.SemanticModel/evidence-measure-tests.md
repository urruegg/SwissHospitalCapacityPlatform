# evidence.SemanticModel — measure validation

Sprint 14.1 T4. DAX queries for the five readiness measures with expected values
on the **current seed catalog** (`docs/bom.yaml` + `docs/region-availability.yaml`,
25 BOM items). DAX cannot be evaluated in the sandbox, so these are the queries a
reviewer runs via the semantic-model MCP / Fabric REST once the model is
published (`deploy`-gated by `approved-to-apply`).

Expected values are reproducible off-Fabric with the pure scorer:

```bash
python3 - <<'PY'
import json, sys
sys.path.insert(0, "data-platform/notebooks/evidence")
from readiness_rules import score_readiness, aggregate_readiness
# run scripts/evidence/publish.py first to materialise data/evidence/*.json
bom  = json.load(open("data/evidence/bom.json"))
deps = json.load(open("data/evidence/dependencies.json"))
avail = json.load(open("data/evidence/region_availability.json"))
by = {}
for e in deps: by.setdefault(e["fromId"], []).append({"to": e["toId"], "type": e["type"]})
items = [{"id": b["id"], "dependsOn": by.get(b["id"], [])} for b in bom]
print(aggregate_readiness(score_readiness(items, avail)))
PY
```

## Queries

| # | Measure | DAX | Expected (current seed) |
| --- | --- | --- | --- |
| 1 | `BOM count` | `EVALUATE ROW("v", [BOM count])` | `25` |
| 2 | `Readiness % (T-SHOW)` | `EVALUATE ROW("v", [Readiness % (T-SHOW)])` | `1.0` (100.0%) |
| 3 | `Readiness % (T-PROD)` | `EVALUATE ROW("v", [Readiness % (T-PROD)])` | `0.84` (84.0%) |
| 4 | `GA-Parity Gap` | `EVALUATE ROW("v", [GA-Parity Gap])` | `4` |
| 5 | `Blocked requirements count` | `EVALUATE ROW("v", [Blocked requirements count])` | `4` |

### S14.3 DoD query — readiness per BOM × region × track for CH North × T-SHOW

```dax
EVALUATE
SUMMARIZECOLUMNS(
    fact_readiness_snapshot[bomId],
    fact_readiness_snapshot[region],
    fact_readiness_snapshot[track],
    FILTER(
        ALL(fact_readiness_snapshot[track]),
        fact_readiness_snapshot[track] = "T-SHOW"
    ),
    FILTER(
        ALL(fact_readiness_snapshot[region]),
        fact_readiness_snapshot[region] = "Switzerland North"
    ),
    "status", MAX(fact_readiness_snapshot[status])
)
```

Returns one `Ready`/`Blocked` status row per BOM item for Switzerland North on
the T-SHOW track (S14.3 acceptance).

## Direct Lake fallback

The measures use `DISTINCTCOUNT` + `CALCULATE` over the Direct Lake fact only;
they return correct values even while the lakehouse is under refresh (Direct Lake
falls back to DirectQuery transparently — no Import partition to go stale).
