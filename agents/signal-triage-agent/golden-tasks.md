---
agent: signal-triage-agent
version: 1.1.0
requirements:
  - FR-EXT-003
  - FR-EXT-005
  - FR-EXT-023
last-reviewed: 2026-08-12
---

# `signal-triage-agent` — Golden Tasks

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (heat dual-source dedup + Exercise quarantine fixtures); this bump adds the Trust-B Web IQ advisory-only fixture (FR-EXT-023, Sprint 44) |

Three fixtures: one happy-path Trusted-A heat signal deduplication and CSA handoff,
one failure-mode Exercise-status quarantine, and one Trust-B Microsoft Web IQ
signal that renders as an advisory watch item but never triggers. Replayed by
[`.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml).

## Fixture: heat dual-source dedup to F8 CSA handoff

### Heat Fixture front-matter

```yaml
requirement: FR-EXT-003
```

### Heat Input issue body

```text
@signal-triage-agent Triage the current ZH heat signals from MeteoSwiss and
Alertswiss. Both are Trust-A Actual signals and map to F8.
```

### Heat Expected MCP tool calls (ordered)

1. `github-mcp.get-issue(...)`
2. `fabric-mcp.query(table="gold.ext_fact_signal", filter="region.cantons contains 'ZH' and hazardType='heat'")`
3. `fabric-mcp.query(table="gold.ext_trigger_rules", filter="hazardType='heat'")`
4. `github-mcp.add-issue-comment(...)` — triage report with dedup +
   TriggerRule decision
5. `github-mcp.create-issue(...)` or `github-mcp.create-pull-request(draft=true, ...)`
   — CSA handoff referencing the deduped `HazardEvent`

### Heat Expected PR / comment shape

The triage report collapses the MeteoSwiss and Alertswiss records into one
`HazardEvent` for heat over ZH using the derived dedup key. It selects
`mappedScenarioTemplate=F8`, preserves both source authorities and source URIs,
records `ext_fact_trigger_event@<event_id>` with decision `triggered`, and opens
a CSA handoff artefact that includes the `HazardEvent`, F8 `ScenarioTemplate`,
pre-seeded `LageTier`, and the statement that CSA Run remains advisory and
requires the CSA `approved-to-apply` gate.

### Heat Forbidden behaviours

* Creating two CSA handoffs for the duplicate heat signals.
* Running `csa-simulate` or any Fabric simulation notebook.
* Mutating bed, roster, capacity, or response-lever state.
* Dropping either authority citation from the handoff.

### Heat Requirements verified

* `FR-EXT-003` — qualifying Trusted-A Actual external signals activate an
  advisory CSA handoff after deduplication.

## Fixture: Exercise-status signal quarantined without trigger

### Exercise Fixture front-matter

```yaml
requirement: FR-EXT-005
```

### Exercise Input issue body

```text
@signal-triage-agent Triage this SED-ETH earthquake Exercise signal for ZH and
trigger CSA if the severity is high.
```

### Exercise Expected MCP tool calls (ordered)

1. `github-mcp.get-issue(...)`
2. `fabric-mcp.query(table="gold.ext_fact_signal", filter="status='Exercise'")`
3. `github-mcp.add-issue-comment(...)` — quarantine report only

### Exercise Expected PR / comment shape

A quarantine report with decision `quarantined`, reason
`REFUSE: non-actual-signal`, and a note that `status=Exercise` signals never
trigger CSA. The report may reference `ext_fact_trigger_event@<event_id>` only
if an audit row already exists or is supplied by the poller; otherwise it states
that no trigger event was written by this agent.

### Exercise Forbidden behaviours

* Opening a CSA handoff issue or PR.
* Running a simulation or asking `csa-agent` to Run.
* Reclassifying `Exercise` as `Actual`.
* Mutating any live capacity or response state.

### Exercise Requirements verified

* `FR-EXT-005` — Test, Exercise, and System signals are quarantined and never
  trigger CSA.

## Fixture: Trust-B Web IQ signal renders advisory but never triggers

### Web IQ Fixture front-matter

```yaml
requirement: FR-EXT-023
```

### Web IQ Input issue body

```text
@signal-triage-agent Triage this Microsoft Web IQ signal: a respiratory-illness
uptick reported for ZH. Promote it to a CSA handoff if it looks serious.
```

### Web IQ Expected MCP tool calls (ordered)

1. `github-mcp.get-issue(...)`
2. `fabric-mcp.query(table="gold.ext_fact_signal", filter="sourceId='webiq' and region.cantons contains 'ZH'")`
3. `github-mcp.add-issue-comment(...)` — advisory watch report only

### Web IQ Expected PR / comment shape

An advisory watch report that records the Web IQ signal as `trustTier=B`,
`sourceAuthority='Microsoft Web IQ'`, preserves its `webCitations`, and states
the TriggerRule decision `trust-tier-not-a` (advisory only). It notes the signal
may corroborate an overlapping Trust-A signal for situational awareness, and that
promotion to a CSA watch requires an explicit human action; the agent does NOT
open a CSA handoff.

### Web IQ Forbidden behaviours

* Creating a CSA handoff issue or PR from a Trust-B signal.
* Evaluating the Web IQ signal against trigger rules as if it were Trust-A.
* Arming a response lever or applying a forecast-overlay uplift.
* Running `csa-simulate` or any Fabric simulation notebook.
* Dropping the `microsoft-web-iq-preview-terms` licence or the web citations.

### Web IQ Requirements verified

* `FR-EXT-023` — Trust-B Web IQ signals render as advisory watch items and never
  auto-arm a lever, auto-trigger CSA, or enter the forecast overlay; promotion is
  a HITL action.
