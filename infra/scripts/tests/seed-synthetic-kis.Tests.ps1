BeforeAll {
    . "$PSScriptRoot/../seed-synthetic-kis.ps1" -DryRun
}

Describe 'seed-synthetic-kis (dry run)' {
    It 'returns the expected one-episode payload in W1 mode' {
        $result = Get-W1SeedPayload
        $result.tableName | Should -Be 'kis.Episode'
        $result.rowCount | Should -Be 1
        $result.row.episode_id | Should -Match '^EP-[0-9]{8}$'
        $result.row.patient_id | Should -Match '^pseudo-[a-z0-9]{16}$'
    }

    It 'refuses to run without -DryRun unless a connection string is supplied' {
        { . "$PSScriptRoot/../seed-synthetic-kis.ps1" } | Should -Throw '*ConnectionString*'
    }
}
