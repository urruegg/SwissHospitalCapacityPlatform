<#
.SYNOPSIS
    Export capacity-dashboard semantic model TMDL from Fabric + verify the 14/12-Active/2-Inactive
    relationship contract (Sprint 09 v2.0.0, T5.5-followup).

.DESCRIPTION
    Sprint 00 Approach A pattern — portal-authored TMDL round-tripped via Fabric REST
    `getDefinition`, then written under the local `.SemanticModel/definition/` folder
    so the authoritative model definition lives in git.

    Handles the Fabric REST Long-Running Operation (LRO) response (202 + Location header)
    by polling until the operation reports Succeeded, then fetching the result.

    After export (or with -VerifyOnly), asserts:
      - Total relationships == 14
      - Inactive relationships == 2
      - The two inactives are the Option B pair (dim_specialty↔dim_hospital and or_case↔or_schedule)

.PARAMETER WorkspaceId
    Fabric workspace GUID. Defaults to Sprint 09 v2 SIT workspace.

.PARAMETER SemanticModelId
    Semantic model item GUID. Defaults to capacity-dashboard in SIT.

.PARAMETER OutputPath
    Local SemanticModel folder to write exported parts into. Fabric REST returns
    part paths already prefixed with 'definition/' (plus '.platform' and
    'definition.pbism' at the root), so the correct target is the SemanticModel
    root, NOT its 'definition/' subfolder. Existing files are overwritten.

.PARAMETER VerifyOnly
    Skip the REST export; run only the relationship-contract verifier against whatever
    TMDL already exists at OutputPath. Useful for CI on pre-committed TMDL.

.PARAMETER SkipVerify
    Run the export but skip the verifier. Useful when re-exporting for a legitimate
    contract change (must be paired with a manual review + updated expected counts).

.EXAMPLE
    ./export_semantic_model_tmdl.ps1

.EXAMPLE
    # CI: verify committed TMDL matches contract without hitting Fabric
    ./export_semantic_model_tmdl.ps1 -VerifyOnly

.NOTES
    Docs:  https://learn.microsoft.com/rest/api/fabric/core/items/get-item-definition
           https://learn.microsoft.com/rest/api/fabric/articles/long-running-operation
    Auth:  az account get-access-token --resource https://api.fabric.microsoft.com
    Spec:  docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md §7
#>

[CmdletBinding()]
param(
    [string]$WorkspaceId = 'f3af9733-9503-4e92-98f9-a901d96f1c87',
    [string]$SemanticModelId = '08245059-a6e7-489f-a765-a3114583db4c',
    [string]$OutputPath = './data-platform/reports/capacity-dashboard.SemanticModel',
    [switch]$VerifyOnly,
    [switch]$SkipVerify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Contract constants (edit here if the model design changes; keep in sync with checkpoint doc) ---
$script:ExpectedTotal    = 27    # Sprint 09: 14; +2 from M2 (encounter→dim_hospital, bed_assignment→dim_hospital); +9 from Sprint 15 BVA; +2 from Sprint 23 org spine (dim_org_unit→dim_hospital, dim_department→dim_org_unit)
$script:ExpectedInactive = 2
$script:ExpectedInactivePairs = @(
    @{ Left = 'dim_specialty'; Right = 'dim_hospital' },
    @{ Left = 'or_case';       Right = 'or_schedule' }
)

# --- S10.11 verifier extension (Sprint 10 M4-A) ---
# Measure count = sum of `measure` blocks across tables/*.tmdl
# Role count    = number of role blocks under roles/*.tmdl (one per file, per TMDL convention)
$script:ExpectedMeasures = 55   # M1 (15): Beds Total, Over-Run Minutes, OR Utilization %, Data Quality Score (Cases),
                                #   Idle-Slot Minutes, Active Encounters, Admissions, Discharged,
                                #   Currently In Hospital, Currently Assigned Beds, Occupancy %,
                                #   Effective Identity UPN, Effective Role Label,
                                #   Effective Hospital, Effective Viewing Label (M1-RLS persona, Sprint 10)
                                # M2 (+3): First-Case On-Time %, Short-Notice Cancellation %, Avg Turnover Minutes
                                # M5 (+7): Beds Free, Forecast Peak 72h, Actual vs Forecast, Turnover,
                                #   Narrative — Bed Manager, Narrative — Ops Lead, Narrative — OR Coordinator
                                # M6 (+2): Benchmark — Cold, Benchmark — Warm
                                # Sprint 15 BVA (+28): all measures under bva_measures.tmdl (Azure consumption,
                                #   budget, value-realization, plan-vs-actual, KPI headlines per persona)
$script:ExpectedRoles    = 8    # BedOps, ORPlanner, Analyst, SemanticOwner (M3-A),
                                # GuestAggregated, SITDemoOperator (M1-RLS, Sprint 10),
                                # BvaExecFull, BvaBoardReadOnly (Sprint 15)

# --- Fabric REST helpers -------------------------------------------------------------------------

function Get-FabricToken {
    try {
        $token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
    }
    catch {
        throw "Failed to acquire Fabric API token. Run 'az login' first. Error: $_"
    }
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "az returned empty token. Check 'az account show' and re-run 'az login'."
    }
    return $token
}

function Invoke-FabricLro {
    <#
      Handles Fabric's Long-Running Operation contract:
        202 Accepted + Location header → poll until Succeeded, then GET the result.
        200 OK with body → return body directly.
      Compatible with Windows PowerShell 5.1 (no -SkipHttpErrorCheck).
    #>
    param(
        [Parameter(Mandatory)][string]$Method,
        [Parameter(Mandatory)][string]$Uri,
        [hashtable]$Headers,
        [string]$Body,
        [int]$PollIntervalSec = 3,
        [int]$MaxPollSec = 120
    )

    $params = @{
        Method      = $Method
        Uri         = $Uri
        Headers     = $Headers
        ContentType = 'application/json'
        UseBasicParsing = $true
    }
    if ($PSBoundParameters.ContainsKey('Body')) { $params.Body = $Body }

    try {
        $response = Invoke-WebRequest @params
    }
    catch {
        $status = $null
        $errBody = $null
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $errBody = $reader.ReadToEnd()
                    $reader.Dispose()
                }
            } catch { }
        }
        throw "Fabric API returned $status : $errBody"
    }

    if ($response.StatusCode -eq 200) {
        return ($response.Content | ConvertFrom-Json)
    }
    if ($response.StatusCode -ne 202) {
        throw "Fabric API returned $($response.StatusCode): $($response.Content)"
    }

    # 202 — poll the operation
    $opLocation = $response.Headers['Location']
    if (-not $opLocation) { throw "202 response missing Location header." }
    if ($opLocation -is [array]) { $opLocation = $opLocation[0] }

    $pollHeaders = @{ Authorization = $Headers.Authorization }

    $waited = 0
    while ($true) {
        Start-Sleep -Seconds $PollIntervalSec
        $waited += $PollIntervalSec
        if ($waited -gt $MaxPollSec) {
            throw "LRO timed out after ${MaxPollSec}s. Operation URI: $opLocation"
        }

        try {
            $poll = Invoke-WebRequest -Method GET -Uri $opLocation -Headers $pollHeaders -UseBasicParsing
        }
        catch {
            throw "LRO poll failed: $($_.Exception.Message)"
        }
        $status = ($poll.Content | ConvertFrom-Json)
        Write-Verbose "LRO status after ${waited}s: $($status.status)"

        switch ($status.status) {
            'Succeeded' {
                # Result URI is exposed via a separate header on the final poll
                $resultLocation = $poll.Headers['Location']
                if ($resultLocation -is [array]) { $resultLocation = $resultLocation[0] }
                if (-not $resultLocation) {
                    # Some operations embed the result in the poll body
                    return $status
                }
                $result = Invoke-WebRequest -Method GET -Uri $resultLocation -Headers $pollHeaders -UseBasicParsing
                return ($result.Content | ConvertFrom-Json)
            }
            'Failed'    { throw "LRO failed: $($status | ConvertTo-Json -Depth 10)" }
            'Cancelled' { throw "LRO cancelled: $($status | ConvertTo-Json -Depth 10)" }
            default     { continue }
        }
    }
}

function Export-SemanticModelDefinition {
    param(
        [Parameter(Mandatory)][string]$WorkspaceId,
        [Parameter(Mandatory)][string]$SemanticModelId,
        [Parameter(Mandatory)][string]$OutputPath
    )

    $token = Get-FabricToken
    $headers = @{ Authorization = "Bearer $token" }
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/semanticModels/$SemanticModelId/getDefinition?format=TMDL"

    Write-Host "GET definition from: $uri" -ForegroundColor Cyan
    $definition = Invoke-FabricLro -Method POST -Uri $uri -Headers $headers -Body '{}'

    if (-not $definition.definition -or -not $definition.definition.parts) {
        throw "Response has no definition.parts. Full response: $($definition | ConvertTo-Json -Depth 10)"
    }

    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $written = 0
    foreach ($part in $definition.definition.parts) {
        if ($part.payloadType -ne 'InlineBase64') {
            Write-Warning "Skipping part '$($part.path)' with unsupported payloadType '$($part.payloadType)'"
            continue
        }
        $bytes = [Convert]::FromBase64String($part.payload)
        $target = Join-Path $OutputPath $part.path
        $targetDir = Split-Path -Parent $target
        if ($targetDir -and -not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        [IO.File]::WriteAllBytes($target, $bytes)
        $written++
        Write-Verbose "wrote: $target ($($bytes.Length) bytes)"
    }
    Write-Host "OK: exported $written parts to $OutputPath" -ForegroundColor Green
}

# --- TMDL relationship-contract verifier ---------------------------------------------------------

function Get-RelationshipRecords {
    <#
      Parse all TMDL files under $Path and return one object per relationship:
        Name       = block identifier (GUID or name)
        FromTable  = table on the many side (fromColumn)
        FromColumn = column on the many side
        ToTable    = table on the one side (toColumn)
        ToColumn   = column on the one side
        IsActive   = $false only if the block contains 'isActive: false'; $true otherwise
        SourceFile = the .tmdl file the block was read from
    #>
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path $Path)) {
        throw "TMDL path not found: $Path"
    }

    $tmdlFiles = Get-ChildItem -Path $Path -Filter '*.tmdl' -Recurse -File
    if (-not $tmdlFiles) {
        throw "No .tmdl files found under $Path"
    }

    $records = @()
    foreach ($file in $tmdlFiles) {
        $lines = Get-Content -LiteralPath $file.FullName
        $current = $null

        foreach ($rawLine in $lines) {
            # Trim only the trailing whitespace; leading tabs matter for TMDL indent semantics
            $line = $rawLine.TrimEnd()

            if ($line -match '^relationship\s+(\S+)') {
                if ($current) { $records += [pscustomobject]$current }
                $current = [ordered]@{
                    Name       = $Matches[1]
                    FromTable  = $null
                    FromColumn = $null
                    ToTable    = $null
                    ToColumn   = $null
                    IsActive   = $true
                    SourceFile = $file.Name
                }
                continue
            }

            if (-not $current) { continue }

            # Top-level (non-indented) content that isn't a property means the block ended.
            # TMDL properties inside a block are tab-indented.
            if ($line -and $line[0] -notmatch '\s' -and $line -notmatch '^\s') {
                $records += [pscustomobject]$current
                $current = $null
                continue
            }

            $trimmed = $line.Trim()
            if ($trimmed -match '^fromColumn:\s*(.+)$') {
                $ref = Split-TmdlColumnRef $Matches[1]
                $current.FromTable  = $ref.Table
                $current.FromColumn = $ref.Column
            }
            elseif ($trimmed -match '^toColumn:\s*(.+)$') {
                $ref = Split-TmdlColumnRef $Matches[1]
                $current.ToTable  = $ref.Table
                $current.ToColumn = $ref.Column
            }
            elseif ($trimmed -match '^isActive:\s*false\b') {
                $current.IsActive = $false
            }
        }
        if ($current) { $records += [pscustomobject]$current }
    }
    return , $records
}

function Split-TmdlColumnRef {
    # TMDL column refs: 'table_name'.'column_name'  or  table_name.column_name
    param([Parameter(Mandatory)][string]$Ref)
    $clean = $Ref.Trim() -replace "^'", '' -replace "'$", ''
    # Split on ".'" (quoted) or plain "." — handle both
    if ($clean -match "^([^']+?)'\.'(.+)$") {
        return @{ Table = $Matches[1]; Column = $Matches[2] }
    }
    if ($clean -match '^([^.]+)\.(.+)$') {
        return @{ Table = ($Matches[1].Trim("'")); Column = ($Matches[2].Trim("'")) }
    }
    return @{ Table = $null; Column = $clean }
}

function Test-RelationshipContract {
    param([Parameter(Mandatory)][string]$Path)

    Write-Host ""
    Write-Host "Verifying relationship contract under: $Path" -ForegroundColor Cyan

    $records = Get-RelationshipRecords -Path $Path
    $total = $records.Count
    $inactive = @($records | Where-Object { -not $_.IsActive })
    $inactiveCount = $inactive.Count
    $activeCount = $total - $inactiveCount

    Write-Host "  Total:    $total  (expected $script:ExpectedTotal)"
    Write-Host "  Active:   $activeCount"
    Write-Host "  Inactive: $inactiveCount  (expected $script:ExpectedInactive)"

    $failures = @()

    if ($total -ne $script:ExpectedTotal) {
        $failures += "Total relationship count $total != expected $script:ExpectedTotal"
    }
    if ($inactiveCount -ne $script:ExpectedInactive) {
        $failures += "Inactive relationship count $inactiveCount != expected $script:ExpectedInactive"
    }

    # Verify Option B pair identity (order-independent match on unordered {left,right} table pairs)
    $observedPairs = $inactive | ForEach-Object {
        $pair = @($_.FromTable, $_.ToTable) | Sort-Object
        ($pair -join '::')
    }
    foreach ($expected in $script:ExpectedInactivePairs) {
        $pair = @($expected.Left, $expected.Right) | Sort-Object
        $key = ($pair -join '::')
        if ($observedPairs -notcontains $key) {
            $failures += "Expected inactive pair not found: $($expected.Left) <-> $($expected.Right)"
        }
    }

    if ($failures.Count -gt 0) {
        Write-Host ""
        Write-Host "CONTRACT FAILED:" -ForegroundColor Red
        $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        Write-Host ""
        Write-Host "Observed inactive relationships:" -ForegroundColor Yellow
        $inactive | Format-Table -AutoSize | Out-String | Write-Host
        exit 4
    }

    Write-Host "OK: 16/14-Active/2-Inactive contract holds." -ForegroundColor Green
}

function Test-MeasureAndRoleContract {
    <#
      S10.11 verifier extension (Sprint 10 M4-A).
      Counts `measure` blocks across tables/*.tmdl and role files under roles/*.tmdl,
      then asserts against the expected constants. Catches drift like the Sprint 09
      portal round-trip that silently dropped 4 role scaffolds.
    #>
    param([Parameter(Mandatory)][string]$Path)

    Write-Host ""
    Write-Host "Verifying measure + role contract under: $Path" -ForegroundColor Cyan

    $tablesDir = Join-Path $Path 'definition/tables'
    $rolesDir  = Join-Path $Path 'definition/roles'

    $measureCount = 0
    if (Test-Path $tablesDir) {
        $measureCount = (Get-ChildItem $tablesDir -Filter '*.tmdl' -File | ForEach-Object {
            @(Select-String -Path $_.FullName -Pattern '^\s*measure\s+').Count
        } | Measure-Object -Sum).Sum
        if (-not $measureCount) { $measureCount = 0 }
    }

    $roleCount = 0
    if (Test-Path $rolesDir) {
        $roleCount = (Get-ChildItem $rolesDir -Filter '*.tmdl' -File).Count
    }

    Write-Host "  Measures: $measureCount  (expected $script:ExpectedMeasures)"
    Write-Host "  Roles:    $roleCount  (expected $script:ExpectedRoles)"

    $failures = @()
    if ($measureCount -ne $script:ExpectedMeasures) {
        $failures += "Measure count $measureCount != expected $script:ExpectedMeasures"
    }
    if ($roleCount -ne $script:ExpectedRoles) {
        $failures += "Role count $roleCount != expected $script:ExpectedRoles"
    }

    if ($failures.Count -gt 0) {
        Write-Host ""
        Write-Host "MEASURE/ROLE CONTRACT FAILED:" -ForegroundColor Red
        $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 5
    }

    Write-Host "OK: $script:ExpectedMeasures measures + $script:ExpectedRoles roles contract holds." -ForegroundColor Green
}

# --- Entry point ---------------------------------------------------------------------------------

if (-not $VerifyOnly) {
    Export-SemanticModelDefinition -WorkspaceId $WorkspaceId -SemanticModelId $SemanticModelId -OutputPath $OutputPath
}

if (-not $SkipVerify) {
    Test-RelationshipContract -Path $OutputPath
    Test-MeasureAndRoleContract -Path $OutputPath
}
