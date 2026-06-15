BeforeAll {
    . "$PSScriptRoot/../configure-fabric.ps1" -DryRun
}

Describe 'configure-fabric (dry run payloads)' {
    It 'workspace payload pins the supplied capacity GUID' {
        $guid = '11111111-2222-3333-4444-555555555555'
        $p = Get-WorkspaceCreatePayload -CapacityId $guid
        $p.capacityId | Should -Be $guid
        $p.displayName | Should -Be 'ws-chhealthpf-sit-data'
    }

    It 'lakehouse payload requests Delta + 3-zone layout via enableSchemas' {
        $p = Get-LakehouseCreatePayload
        $p.displayName | Should -Be 'lh_chhealthpf_sit'
        $p.creationPayload.enableSchemas | Should -Be $true
    }

    It 'mirror payload base64-encodes mirroring.json with AzureSqlDatabase source + Delta target' {
        $connectionId = '66666666-7777-8888-9999-000000000000'
        $p = Get-MirrorCreatePayload -ConnectionId $connectionId -Database 'kis'

        $p.displayName | Should -Be 'mir_chhealthpf_kis'
        $part = $p.definition.parts[0]
        $part.path | Should -Be 'mirroring.json'
        $part.payloadType | Should -Be 'InlineBase64'

        $json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($part.payload))
        $obj = $json | ConvertFrom-Json

        $obj.properties.source.type | Should -Be 'AzureSqlDatabase'
        $obj.properties.source.typeProperties.connection | Should -Be $connectionId
        $obj.properties.source.typeProperties.database | Should -Be 'kis'

        $obj.properties.target.type | Should -Be 'MountedRelationalDatabase'
        $obj.properties.target.typeProperties.format | Should -Be 'Delta'
    }
}
