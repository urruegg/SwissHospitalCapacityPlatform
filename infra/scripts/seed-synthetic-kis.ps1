#Requires -Version 5.1

<#
.SYNOPSIS
    Sprint-08 W1.1 walking-skeleton seed for the synthetic KIS source DB.

.DESCRIPTION
    Loads exactly one synthetic episode row into the kis.Episode table of the
    Azure SQL source database provisioned by the source-sql Bicep module.

    The intent is the walking-skeleton end-to-end path
    (source -> bronze -> silver -> gold -> semantic), not volume or fidelity.
    PHI is forbidden in SIT per ADR-0003 / ADR-0004; all data here is synthetic.

.PARAMETER ConnectionString
    ADO.NET-style connection string for the target Azure SQL database. The
    connection should use Entra ID + managed identity in real runs; password-
    based connection strings must only be used for local dev against the
    emulator and must never be persisted. Required unless -DryRun is set.

.PARAMETER DryRun
    When set, the script does not connect to SQL. It returns the plan-only
    seed payload describing what would be inserted. Used by Pester tests and
    by pre-deploy verification.

.NOTES
    Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
    Module: infra/modules/data-platform/source-sql
    Tests:  infra/scripts/tests/seed-synthetic-kis.Tests.ps1
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ConnectionString,

    [Parameter()]
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-W1SeedPayload {
    return @{
        tableName = 'kis.Episode'
        rowCount  = 1
        row       = @{
            episode_id   = 'EP-00000001'
            patient_id   = 'pseudo-a1b2c3d4e5f60718'
            admit_ts     = '2026-06-14T08:00:00Z'
            discharge_ts = $null
            ward         = 'INT-A'
            source       = 'walking-skeleton'
        }
    }
}

function Invoke-W1Seed {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ConnectionString
    )

    $payload = Get-W1SeedPayload

    $ddl = @'
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'kis')
    EXEC('CREATE SCHEMA kis');
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Episode' AND schema_id = SCHEMA_ID('kis'))
    CREATE TABLE kis.Episode (
        episode_id   NVARCHAR(32)  NOT NULL CONSTRAINT PK_Episode PRIMARY KEY,
        patient_id   NVARCHAR(64)  NOT NULL,
        admit_ts     DATETIME2(0)  NOT NULL,
        discharge_ts DATETIME2(0)  NULL,
        ward         NVARCHAR(32)  NOT NULL,
        source       NVARCHAR(64)  NOT NULL
    );
'@

    Invoke-Sqlcmd -ConnectionString $ConnectionString -Query $ddl

    $merge = @"
MERGE kis.Episode AS target
USING (
    SELECT
        '`$(episode_id)'                       AS episode_id,
        '`$(patient_id)'                       AS patient_id,
        CAST('`$(admit_ts)' AS DATETIME2(0))   AS admit_ts,
        NULLIF('`$(discharge_ts)', '')         AS discharge_ts,
        '`$(ward)'                             AS ward,
        '`$(source)'                           AS source
) AS src
  ON target.episode_id = src.episode_id
WHEN MATCHED THEN UPDATE SET
    patient_id   = src.patient_id,
    admit_ts     = src.admit_ts,
    discharge_ts = src.discharge_ts,
    ward         = src.ward,
    source       = src.source
WHEN NOT MATCHED THEN INSERT
    (episode_id, patient_id, admit_ts, discharge_ts, ward, source)
    VALUES (src.episode_id, src.patient_id, src.admit_ts, src.discharge_ts, src.ward, src.source);
"@

    $dischargeValue = if ($null -eq $payload.row.discharge_ts) { '' } else { [string]$payload.row.discharge_ts }

    $variables = @(
        "episode_id=$($payload.row.episode_id)",
        "patient_id=$($payload.row.patient_id)",
        "admit_ts=$($payload.row.admit_ts)",
        "discharge_ts=$dischargeValue",
        "ward=$($payload.row.ward)",
        "source=$($payload.row.source)"
    )

    Invoke-Sqlcmd -ConnectionString $ConnectionString -Query $merge -Variable $variables

    return [pscustomobject]@{
        DryRun      = $false
        RowsPlanned = $payload.rowCount
        Target      = $payload.tableName
    }
}

if ($DryRun) {
    return Get-W1SeedPayload
}

if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
    throw 'ConnectionString is required when -DryRun is not specified.'
}

Invoke-W1Seed -ConnectionString $ConnectionString
