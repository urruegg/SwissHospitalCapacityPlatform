#Requires -Version 5.1
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.0.0' }

BeforeAll {
    $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'Resume-FabricCapacity.ps1'
}

Describe 'Resume-FabricCapacity' {

    BeforeEach {
        # Default mock — represents a Paused capacity that will be resumed.
        Mock -CommandName az -MockWith {
            $joined = $args -join ' '
            if ($joined -match 'resource invoke-action.*--action resume') {
                return '{"status": "Active"}'
            }
            if ($joined -match 'resource show') {
                return '{"properties": {"state": "Paused"}}'
            }
            return '{}'
        }
    }

    It 'exists as a file' {
        Test-Path $script:ScriptPath | Should -Be $true
    }

    It 'accepts -Environment param (sit|prod)' {
        $cmd = Get-Command $script:ScriptPath
        $cmd.Parameters.ContainsKey('Environment') | Should -Be $true
        $validate = $cmd.Parameters['Environment'].Attributes |
            Where-Object { $_ -is [System.Management.Automation.ValidateSetAttribute] }
        $validate | Should -Not -BeNullOrEmpty
        $validate.ValidValues | Should -Contain 'sit'
        $validate.ValidValues | Should -Contain 'prod'
    }

    It 'accepts -SubscriptionId param' {
        $cmd = Get-Command $script:ScriptPath
        $cmd.Parameters.ContainsKey('SubscriptionId') | Should -Be $true
    }

    It 'calls az with --action resume for SIT' {
        & $script:ScriptPath -Environment sit
        Should -Invoke -CommandName az -ParameterFilter { ($args -join ' ') -match '--action resume' } -Times 1
    }

    It 'targets correct capacity ID for SIT' {
        & $script:ScriptPath -Environment sit
        Should -Invoke -CommandName az -ParameterFilter {
            $joined = $args -join ' '
            ($joined -match 'fabricihzhhpfsit') -and ($joined -match '--action resume')
        } -Times 1
    }

    It 'targets correct capacity ID for PROD' {
        & $script:ScriptPath -Environment prod
        Should -Invoke -CommandName az -ParameterFilter {
            $joined = $args -join ' '
            ($joined -match 'fabricihzhhpfprod') -and ($joined -match '--action resume')
        } -Times 1
    }

    It 'is idempotent — no resume call when already Active' {
        Mock -CommandName az -MockWith {
            $joined = $args -join ' '
            if ($joined -match 'resource show') {
                return '{"properties": {"state": "Active"}}'
            }
            return '{}'
        }
        { & $script:ScriptPath -Environment sit } | Should -Not -Throw
        Should -Invoke -CommandName az -ParameterFilter { ($args -join ' ') -match '--action resume' } -Times 0 -Exactly
    }

    It 'targets the resource group rg-ihzhhpf-<env>' {
        & $script:ScriptPath -Environment sit
        Should -Invoke -CommandName az -ParameterFilter {
            ($args -join ' ') -match 'rg-ihzhhpf-sit'
        } -Times 1
    }
}
