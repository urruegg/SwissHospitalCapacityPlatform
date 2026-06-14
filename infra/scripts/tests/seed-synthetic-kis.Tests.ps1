#Requires -Version 5.1
#Requires -Modules @{ ModuleName = 'Pester'; ModuleVersion = '5.0' }

# Pester tests for the W1.1 synthetic-KIS seed script.
# Run from repo root:
#   Invoke-Pester -Path infra/scripts/tests/seed-synthetic-kis.Tests.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'seed-synthetic-kis.ps1' {
    BeforeAll {
        $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'seed-synthetic-kis.ps1'
        $script:ScriptPath = (Resolve-Path $script:ScriptPath).Path
        . $script:ScriptPath
    }

    Context 'Get-W1SeedPayload' {
        It 'returns exactly one episode row with the expected shape' {
            $payload = Get-W1SeedPayload
            $payload | Should -Not -BeNullOrEmpty
            @($payload).Count | Should -Be 1

            $row = @($payload)[0]
            $row.EpisodeId | Should -Not -BeNullOrEmpty
            $row.PatientId | Should -Not -BeNullOrEmpty
            $row.AdmissionTimestamp | Should -BeOfType ([datetime])
            $row.Ward | Should -Not -BeNullOrEmpty
        }
    }

    Context 'Invoke-W1Seed' {
        It 'throws when ConnectionString is missing' {
            { Invoke-W1Seed -ConnectionString '' -DryRun } |
                Should -Throw -ErrorId '*ConnectionString*'
        }

        It 'returns a dry-run report without contacting SQL when -DryRun is set' {
            $report = Invoke-W1Seed -ConnectionString 'Server=tcp:fake;Database=kis;' -DryRun
            $report.DryRun | Should -BeTrue
            $report.RowsPlanned | Should -Be 1
            $report.Target | Should -Match 'kis\.Episode'
        }
    }
}
