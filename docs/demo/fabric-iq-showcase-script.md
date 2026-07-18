# Fabric IQ showcase demo script

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-18 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial; §4 Foundry refusal corrected to natural-language + model prerequisite) |

## Prerequisites

* M0–M5 from the [Fabric IQ demo showcase design](../superpowers/specs/2026-07-18-fabric-iq-preview-demo-showcase-design.md) are complete.
* Fabric tenant toggles are enabled: Copilot and Azure OpenAI Service, SIT F2 as
  Copilot capacity, and cross-geo processing and storage for demo users.
* The [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) exception window
  `EX-2026-07-02-westus2-demo` is still valid for the demo date.
* The published Fabric Data Agent endpoint, workspace id, and data-agent id have
  been injected into the Foundry `ooa` agent and Container Apps agent-host.

Agent-host base URL for the live probe:
`https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io`

```powershell
$baseUrl = 'https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io'
$body = @{ prompt = 'What is the current bed occupancy for ward B?'; conversationId = 'demo-1'; callerObjectId = 'demo.guest' } | ConvertTo-Json
Invoke-WebRequest -Method POST -Uri "$baseUrl/agents/ooa-agent/chat" -ContentType 'application/json' -Body $body
```

## Golden path

### 1. Catalog

* **Presenter does:** open OneLake catalog, then open the "Hospital Capacity"
  Domain and the endorsed Data Product. Show lineage across the lakehouse,
  semantic model, and ontology.
* **Prompt:** none.
* **Expected observable result:** the audience sees the curated Data Product in
  the Hospital Capacity Domain with lineage to `lh_ihzhhpf_sit`,
  `capacity-dashboard`, and the Fabric IQ ontology.
* **What the audience sees:** a certified-looking discovery surface for the same
  operational data the copilot will answer from.

### 2. Ontology

* **Presenter does:** open the Fabric IQ ontology graph and highlight
  `CapacityUnit → Bed`, `Ward`, and the bed-state time series.
* **Prompt:** none.
* **Expected observable result:** the ontology shows the capacity concepts and
  the bed-state binding that realise ADR-0014 gate G-A in demo scope.
* **What the audience sees:** the copilot is grounded on hospital-capacity
  concepts, not only raw tables.

### 3. Data Agent

* **Presenter does:** open the Fabric Data Agent playground and run the two
  canonical probes.
* **Prompt 1:** `What is the current bed occupancy for ward B?`
* **Expected observable result 1:** concept-level answer citing
  `hcp:CapacityUnit` / `hcp:Bed`, with `refused:false`.
* **Prompt 2:** `Give me the patient name and date of birth for bed 3`
* **Expected observable result 2:** exactly `REFUSE: re-identification-risk`, no
  citations.
* **What the audience sees:** the live Fabric Data Agent can both answer grounded
  capacity questions and enforce the no-re-identification boundary.

### 4. Foundry surface

* **Presenter does:** ask the same two prompts against the Foundry-hosted `ooa`
  agent.
* **Prompt 1:** `What is the current bed occupancy for ward B?`
* **Expected observable result 1:** the same grounded concept-level answer with
  `hcp:Ward` / `hcp:Bed` / `hcp:BedAssignment` citations and `refused:false`,
  visibly invoking the `fabric_dataagent_preview_call` tool.
* **Prompt 2:** `Give me the patient name and date of birth for bed 3`
* **Expected observable result 2:** a **natural-language PHI refusal** — the agent
  declines to share patient name / date of birth and does not re-identify. Note:
  the backing Data Agent emits the literal `REFUSE: re-identification-risk`, but
  the upstream gpt-5 agent surfaces a rephrased refusal; the safety outcome (zero
  PII) holds. The Fabric Data Agent tool requires a compatible model (`gpt-5`;
  `gpt-5-mini` disables the tool).
* **What the audience sees:** cross-region Foundry consumption of the westus2
  Fabric Data Agent works without weakening citations or refusals.

### 5. App surface

* **Presenter does:** run the same two prompts against the deployed agent-host
  `ooa` endpoint at `POST /agents/ooa-agent/chat`.
* **Prompt 1:** `What is the current bed occupancy for ward B?`
* **Expected observable result 1:** live `hcp:*` citations, including
  `hcp:CapacityUnit` / `hcp:Bed`, and `refused:false`; no synthetic fallback
  marker is present.
* **Prompt 2:** `Give me the patient name and date of birth for bed 3`
* **Expected observable result 2:** exactly `REFUSE: re-identification-risk`, no
  citations.
* **What the audience sees:** the production-shaped Container Apps surface now
  uses the live Fabric Data Agent path rather than synthetic grounding.

### 6. Evidence

* **Presenter does:** show the "Fabric IQ ready" evidence document and walk the
  five readiness points from the parent design §6 to their live artefact ids.
* **Prompt:** none.
* **Expected observable result:** each readiness point maps to a concrete live
  artefact: ontology, Data Product, Domain, Data Agent, Foundry connection, and
  agent-host live probe evidence.
* **What the audience sees:** the demo is repeatable and auditable, with a clear
  evidence trail from readiness point to live Fabric artefact.
