# Sprint 12 completion — MCAPS demo-user model (ADR-0027).
#
# Adds admin@ + urruegg@ as members of ALL 17 HCC.* security groups, so both
# accounts carry every persona-role for demo purposes. Because the Microsoft.Graph/users
# Bicep type is read-only (Microsoft Learn: intentionally so at v1.0 and beta),
# persona users are NOT provisioned in SIT — the two operator accounts stand in
# for all 23 personas.
#
# Idempotent: memberships that already exist are logged as `already-member (skip)`.
# Safe to re-run after a re-deploy of the entra module (with sit-groups-only.bicepparam).
#
# Reference: ADR-0027 (docs/adr/0027-mcaps-demo-users-full-group-membership.md)

$adminUpn   = 'admin@mngenvmcap164444.onmicrosoft.com'
$urrueggUpn = 'urruegg@MngEnvMCAP164444.onmicrosoft.com'

# Resolve objectIds at runtime — avoids hard-coding tenant-specific GUIDs.
Write-Host "Resolving user objectIds..."
$adminId   = (az ad user show --id $adminUpn   --query id -o tsv)
$urrueggId = (az ad user show --id $urrueggUpn --query id -o tsv)
if (-not $adminId -or -not $urrueggId) {
  Write-Host "ERROR: could not resolve one or both user UPNs. adminId=$adminId urrueggId=$urrueggId"
  exit 1
}
Write-Host "  admin@   -> $adminId"
Write-Host "  urruegg@ -> $urrueggId"

$groups = @(
  'HCC.AIGovernance','HCC.Auditor','HCC.BedManager','HCC.CantonalViewer',
  'HCC.CrisisManager','HCC.DemoOperator','HCC.DischargeCoordinator','HCC.EDLead',
  'HCC.Executive','HCC.FlowManager','HCC.GuestReadOnly','HCC.OntologySteward',
  'HCC.OperationsLead','HCC.ORCoordinator','HCC.PlatformAdmin','HCC.StaffingCoordinator',
  'HCC.SuperAdmin'
)

$members = @(
  @{ upn = 'admin@';   id = $adminId },
  @{ upn = 'urruegg@'; id = $urrueggId }
)

$total = 0; $added = 0; $skipped = 0; $failed = 0
foreach ($g in $groups) {
  foreach ($m in $members) {
    $total++
    Write-Host "[$total/$($groups.Count * $members.Count)] $($m.upn) -> $g ..." -NoNewline
    $out = & az ad group member add --group $g --member-id $m.id 2>&1
    $code = $LASTEXITCODE
    if ($code -eq 0) {
      Write-Host ' added'
      $added++
    }
    elseif ($out -match 'One or more added object references already exist|already used|already exist') {
      Write-Host ' already-member (skip)'
      $skipped++
    }
    else {
      Write-Host ' FAILED'
      Write-Host "    $out"
      $failed++
    }
  }
}

Write-Host ''
Write-Host "Summary: total=$total added=$added skipped=$skipped failed=$failed"
if ($failed -gt 0) { exit 1 }
