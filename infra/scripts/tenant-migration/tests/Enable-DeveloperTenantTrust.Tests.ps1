#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'Enable-DeveloperTenantTrust.ps1'
}

Describe 'Enable-DeveloperTenantTrust' {
    It 'exists and is a script file' {
        Test-Path $script:ScriptPath | Should -BeTrue
    }
    It 'declares mandatory parameter TenantId as a GUID' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'TenantId' }
        $param | Should -Not -BeNullOrEmpty
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'supports -WhatIf via SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'enables the Azure CLI WAM broker' {
        Select-String -Path $script:ScriptPath -Pattern 'az config set core\.enable_broker_on_windows=true' -Quiet | Should -BeTrue
    }
    It 'signs in via az login --tenant <TenantId>' {
        Select-String -Path $script:ScriptPath -Pattern 'az login --tenant' -Quiet | Should -BeTrue
    }
    It 'signs in via Connect-AzAccount' {
        Select-String -Path $script:ScriptPath -Pattern 'Connect-AzAccount' -Quiet | Should -BeTrue
    }
    It 'falls back to device-code with a warning when broker is unavailable' {
        Select-String -Path $script:ScriptPath -Pattern '--use-device-code' -Quiet | Should -BeTrue
    }
    It 'prints Workplace Join guidance' {
        Select-String -Path $script:ScriptPath -Pattern 'Access work or school' -Quiet | Should -BeTrue
    }
    It 'validates by calling az account show and Get-AzContext post sign-in' {
        Select-String -Path $script:ScriptPath -Pattern 'az account show' -Quiet | Should -BeTrue
        Select-String -Path $script:ScriptPath -Pattern 'Get-AzContext' -Quiet | Should -BeTrue
    }
}
