# capacity-dashboard.Report

Power BI PBIP report for Sprint 09 v2.0.0 dashboard (design spec §6).

## Status

**Skeleton only.** Full report authored via **Fabric portal / Power BI Desktop**, exported via REST `getDefinition`. Skeleton provides:

- `.pbip` root pointer + `.pbir` semantic-model connection
- Page manifests (`pages/pages.json`)
- Empty `visualContainers[]` per page
- Detailed layout READMEs per page mapping to design spec §6.1 / §6.2

## Authoring workflow

1. Open [`../capacity-dashboard.pbip`](../capacity-dashboard.pbip) in Power BI Desktop.
2. Confirm both pages in `pages/pages.json` load with empty canvas.
3. Follow `pages/page-bed-manager/README.md` and `pages/page-or-coordinator/README.md`.
4. Publish to workspace `ws-ihzhhpf-<env>`.
5. Export the finalized PBIP via `data-platform/scripts/deploy_report.ps1 -Region westus2 -WorkspaceId <id> -DryRun`.
6. Commit the exported `page.json` files with populated `visualContainers[]`.

## Related
- Semantic model: [`../capacity-dashboard.SemanticModel/`](../capacity-dashboard.SemanticModel/)
- OR sample data: [`../../../data/synthetic/or-samples/`](../../../data/synthetic/or-samples/)
- OR loader notebook: [`../notebooks/reference/04_load_or_samples.ipynb`](../notebooks/reference/04_load_or_samples.ipynb)
- Deploy script: [`../scripts/deploy_report.ps1`](../scripts/deploy_report.ps1)
