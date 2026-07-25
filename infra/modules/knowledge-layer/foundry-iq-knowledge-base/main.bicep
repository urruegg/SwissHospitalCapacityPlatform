// Sprint 28 WS-INF (#377) — Foundry IQ Knowledge Base marker module.
//
// The Foundry IQ Knowledge Layer (knowledge sources + knowledge base + agentic
// retrieval) is NOT a Bicep/ARM-provisionable resource type — it is created over
// the GA Azure AI Search substrate (see `../ai-search/main.bicep`) via the Search
// data-plane REST API and the Foundry IQ portal (design D2, ADR-0043; some
// surfaces Preview per design R2). This module is therefore a thin MARKER that
// records the naming + pinned-version contract the operator runbook
// (`knowledge-base-rest.md`) consumes, mirroring the OneLake-shortcut pattern in
// `data-foundation/masterdata-landing`. It provisions no resources.

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod. Used to derive the knowledge-source / knowledge-base names in the runbook.')
@minLength(3)
param nameSuffix string

@description('Pinned data-plane Search REST api-version for agentic retrieval. Threaded from the ai-search module output so a single reviewed version is used everywhere.')
param searchRestApiVersion string = '2024-05-01-preview'

// Naming contract consumed by knowledge-base-rest.md (kept as outputs so the
// composition root and runbook agree on a single source of truth).
var knowledgeSourceName = toLower('ks-curavias-corpus-${nameSuffix}')
var knowledgeBaseName = toLower('kb-curavias-po-${nameSuffix}')

@description('Foundry IQ knowledge-base module marker (no resources; provisioned via knowledge-base-rest.md).')
output moduleStatus string = 'knowledge-layer-foundry-iq-knowledge-base-marker'

@description('Knowledge source name (Class A corpus) the runbook creates against AI Search.')
output knowledgeSourceName string = knowledgeSourceName

@description('Knowledge base name the PO Agent domain #1 binds to.')
output knowledgeBaseName string = knowledgeBaseName

@description('Pinned data-plane Search REST api-version echoed for the runtime.')
output searchRestApiVersion string = searchRestApiVersion
