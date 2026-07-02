#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'Grant-SubscriptionRbac.ps1'
}

Describe 'Grant-SubscriptionRbac' {
    It 'exists' { Test-Path $script:ScriptPath | Should -BeTrue }
    It 'has SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'declares mandatory PrincipalId as guid' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'PrincipalId' }
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'declares mandatory SubscriptionId as guid' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'SubscriptionId' }
        $param.Attributes.TypeName.FullName | Should -Contain 'guid'
    }
    It 'declares RoleName with default Contributor' {
        Select-String -Path $script:ScriptPath -Pattern '\$RoleName\s*=\s*[''"]Contributor[''"]' -Quiet | Should -BeTrue
    }
    It 'pre-checks with Get-AzRoleAssignment to avoid duplicate assignment' {
        Select-String -Path $script:ScriptPath -Pattern 'Get-AzRoleAssignment' -Quiet | Should -BeTrue
    }
    It 'uses New-AzRoleAssignment to assign' {
        Select-String -Path $script:ScriptPath -Pattern 'New-AzRoleAssignment' -Quiet | Should -BeTrue
    }
}
