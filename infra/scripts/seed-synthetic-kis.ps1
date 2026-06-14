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
    emulator and must never be persisted.

.PARAMETER DryRun
    When set, the function does not connect to SQL. It returns a plan-only
    report describing what would be inserted. Used by Pester tests and by
    pre-deploy verification.

.NOTES
    Spec: docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
    Module: infra/modules/data-platform/source-sql
    Tests:  infra/scripts/tests/seed-synthetic-kis.Tests.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-W1SeedPayload {
    [CmdletBinding()]
    [OutputType([object[]])]
    param()

    $row = [pscustomobject]@{
        EpisodeId          = 'EP-W1-0001'
        PatientId          = 'PT-W1-0001'
        AdmissionTimestamp = [datetime]::new(2026, 6, 12, 8, 30, 0, [System.DateTimeKind]::Utc)
        Ward               = 'WARD-A1'
    }

    return ,@($row)
}

function Invoke-W1Seed {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$ConnectionString,

        [Parameter()]
        [switch]$DryRun
    )

    if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
        Write-Error -Message 'ConnectionString is required.' -ErrorId 'ConnectionStringMissing' -Category InvalidArgument -ErrorAction Stop
    }

    $payload = Get-W1SeedPayload
    $target = 'kis.Episode'

    if ($DryRun) {
        return [pscustomobject]@{
            DryRun      = $true
            RowsPlanned = @($payload).Count
            Target      = $target
            Payload     = $payload
        }
    }

    Write-Verbose "Connecting to SQL with connection string of length $($ConnectionString.Length) to seed $target."

    $connection = New-Object System.Data.SqlClient.SqlConnection $ConnectionString
    $rowsWritten = 0
    try {
        $connection.Open()
        foreach ($row in $payload) {
            $command = $connection.CreateCommand()
            $command.CommandText = @"
MERGE kis.Episode AS target
USING (SELECT @EpisodeId AS EpisodeId, @PatientId AS PatientId, @AdmissionTimestamp AS AdmissionTimestamp, @Ward AS Ward) AS src
  ON (target.EpisodeId = src.EpisodeId)
WHEN MATCHED THEN UPDATE SET PatientId = src.PatientId, AdmissionTimestamp = src.AdmissionTimestamp, Ward = src.Ward
WHEN NOT MATCHED THEN INSERT (EpisodeId, PatientId, AdmissionTimestamp, Ward) VALUES (src.EpisodeId, src.PatientId, src.AdmissionTimestamp, src.Ward);
"@
            [void]$command.Parameters.AddWithValue('@EpisodeId', $row.EpisodeId)
            [void]$command.Parameters.AddWithValue('@PatientId', $row.PatientId)
            [void]$command.Parameters.AddWithValue('@AdmissionTimestamp', $row.AdmissionTimestamp)
            [void]$command.Parameters.AddWithValue('@Ward', $row.Ward)
            $rowsWritten += $command.ExecuteNonQuery()
        }
    }
    finally {
        if ($connection.State -ne [System.Data.ConnectionState]::Closed) {
            $connection.Close()
        }
        $connection.Dispose()
    }

    return [pscustomobject]@{
        DryRun       = $false
        RowsPlanned  = @($payload).Count
        RowsAffected = $rowsWritten
        Target       = $target
    }
}
