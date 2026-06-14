BeforeAll {
    . "$PSScriptRoot/../configure-fabric.ps1" -DryRun
}

Describe 'configure-fabric (dry run payloads)' {
    It 'workspace payload pins the right capacity and region' {
        $p = Get-WorkspaceCreatePayload -CapacityId 'fabric-chhealthpf-sit' -Region 'switzerlandnorth'
        $p.capacityId | Should -Be 'fabric-chhealthpf-sit'
        $p.displayName | Should -Be 'ws-chhealthpf-sit-data'
    }

    It 'lakehouse payload requests Delta + 3-zone layout' {
        $p = Get-LakehouseCreatePayload
        $p.displayName | Should -Be 'lh_chhealthpf_sit'
        $p.creationPayload.enableSchemas | Should -Be $true
    }

    It 'mirror payload binds source server + database + KIS schema' {
        $p = Get-MirrorCreatePayload -ServerFqdn 'sql-chhealthpf-sit.database.windows.net' -Database 'kis'
        $p.displayName | Should -Be 'mir_chhealthpf_kis'
        $p.sourceConnection.server | Should -Be 'sql-chhealthpf-sit.database.windows.net'
        $p.sourceConnection.database | Should -Be 'kis'
        $p.sourceConnection.schemas | Should -Contain 'kis'
    }
}
