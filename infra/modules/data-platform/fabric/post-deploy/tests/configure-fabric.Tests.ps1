BeforeAll {
    . "$PSScriptRoot/../configure-fabric.ps1" -DryRun
}

Describe 'configure-fabric (dry run payloads)' {
    It 'workspace payload pins the supplied capacity GUID' {
        $guid = '11111111-2222-3333-4444-555555555555'
        $p = Get-WorkspaceCreatePayload -CapacityId $guid
        $p.capacityId | Should -Be $guid
        $p.displayName | Should -Be 'ws-ihzhhpf-sit-data'
    }

    It 'lakehouse payload requests Delta + 3-zone layout via enableSchemas' {
        $p = Get-LakehouseCreatePayload
        $p.displayName | Should -Be 'lh_ihzhhpf_sit'
        $p.creationPayload.enableSchemas | Should -Be $true
    }

    It 'mirror payload base64-encodes mirroring.json with AzureSqlDatabase source + Delta target' {
        $connectionId = '66666666-7777-8888-9999-000000000000'
        $p = Get-MirrorCreatePayload -ConnectionId $connectionId -Database 'kis'

        $p.displayName | Should -Be 'mir_ihzhhpf_kis'
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

Describe 'Get-SemanticModelCreatePayload' {
    BeforeAll {
        $script:wsId = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        $script:lhId = '11111111-2222-3333-4444-555555555555'
        $script:payload = Get-SemanticModelCreatePayload -WorkspaceId $wsId -LakehouseId $lhId
    }

    It 'declares the item as a Direct Lake semantic model' {
        $payload.displayName | Should -Be 'sm_capacity_data_product'
        $payload.type        | Should -Be 'SemanticModel'
        $payload.definition.format | Should -Be 'tmdl'
    }

    It 'carries exactly the four TMDL parts in the expected paths' {
        $paths = $payload.definition.parts | ForEach-Object { $_.path } | Sort-Object
        $paths | Should -Be @(
            'definition/database.tmdl',
            'definition/dataSources.tmdl',
            'definition/model.tmdl',
            'definition/tables/demand_encounter.tmdl'
        )
        $payload.definition.parts | ForEach-Object { $_.payloadType | Should -Be 'InlineBase64' }
    }

    It 'base64-encodes every part so it round-trips back to UTF-8 text' {
        foreach ($part in $payload.definition.parts) {
            { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($part.payload)) } | Should -Not -Throw
        }
    }

    It 'substitutes both OneLake GUID placeholders into dataSources.tmdl' {
        $part = $payload.definition.parts | Where-Object { $_.path -eq 'definition/dataSources.tmdl' }
        $text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($part.payload))
        $text | Should -Match ([Regex]::Escape($wsId))
        $text | Should -Match ([Regex]::Escape($lhId))
        $text | Should -Not -Match '\[WORKSPACE_GUID\]'
        $text | Should -Not -Match '\[LAKEHOUSE_GUID\]'
    }

    It 'binds the table partition to gold.demand_encounter with the Encounter Count measure' {
        $part = $payload.definition.parts | Where-Object { $_.path -eq 'definition/tables/demand_encounter.tmdl' }
        $text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($part.payload))
        $text | Should -Match "source = entity 'gold.demand_encounter'"
        $text | Should -Match "measure 'Encounter Count'"
    }

    It 'never exposes patient_id (least-disclosure invariant)' {
        foreach ($part in $payload.definition.parts) {
            $text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($part.payload))
            $text | Should -Not -Match 'patient_id'
        }
    }
}
