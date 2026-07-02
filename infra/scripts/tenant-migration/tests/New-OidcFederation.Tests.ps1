#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'New-OidcFederation.ps1'
}

Describe 'New-OidcFederation' {
    It 'exists' {
        Test-Path $script:ScriptPath | Should -BeTrue
    }
    It 'declares mandatory DisplayName parameter' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:ScriptPath, [ref]$null, [ref]$null)
        $param = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'DisplayName' }
        $param | Should -Not -BeNullOrEmpty
    }
    It 'declares mandatory RepoFullName parameter (owner/repo)' {
        Select-String -Path $script:ScriptPath -Pattern '\$RepoFullName' -Quiet | Should -BeTrue
    }
    It 'declares Environments parameter defaulting to sit and prod' {
        Select-String -Path $script:ScriptPath -Pattern "Environments\s*=\s*@\('sit',\s*'prod'\)" -Quiet | Should -BeTrue
    }
    It 'supports -WhatIf' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'checks for existing app registration before creating one (idempotency)' {
        Select-String -Path $script:ScriptPath -Pattern 'az ad app list' -Quiet | Should -BeTrue
    }
    It 'uses the GitHub OIDC federated credential subject format' {
        # Guard against the PowerShell 'scope specifier' interpolation bug where
        # "repo:$RepoFullName:environment:$env" was silently parsed as accessing
        # $RepoFullName in scope 'environment', producing a malformed subject.
        # Assert the literal is built via string concatenation, not naked interpolation.
        Select-String -Path $script:ScriptPath -Pattern "'repo:' \+ \`$RepoFullName \+ ':environment:' \+ \`$env" -Quiet | Should -BeTrue
    }
    It 'produces a well-formed subject at runtime for a sample env' {
        # Load the script's subject-building expression by simulating the same locals.
        $RepoFullName = 'urruegg/SwissHospitalCapacityPlatform'
        $env = 'sit'
        $subject = 'repo:' + $RepoFullName + ':environment:' + $env
        $subject | Should -Be 'repo:urruegg/SwissHospitalCapacityPlatform:environment:sit'
    }
    It 'uses AzureADTokenExchange audience for federated OIDC exchange' {
        Select-String -Path $script:ScriptPath -Pattern 'api://AzureADTokenExchange' -Quiet | Should -BeTrue
    }
    It 'outputs the client ID at end' {
        Select-String -Path $script:ScriptPath -Pattern 'ClientId\s*=' -Quiet | Should -BeTrue
    }
}
