#Requires -Modules Pester
BeforeAll {
    $script:ScriptPath = Join-Path (Join-Path $PSScriptRoot '..') 'Set-GithubEnvironmentConfig.ps1'
}

Describe 'Set-GithubEnvironmentConfig' {
    It 'exists' { Test-Path $script:ScriptPath | Should -BeTrue }
    It 'has SupportsShouldProcess' {
        Select-String -Path $script:ScriptPath -Pattern 'SupportsShouldProcess' -Quiet | Should -BeTrue
    }
    It 'declares mandatory RepoFullName' {
        Select-String -Path $script:ScriptPath -Pattern '\$RepoFullName' -Quiet | Should -BeTrue
    }
    It 'declares Environment parameter' {
        Select-String -Path $script:ScriptPath -Pattern '\$Environment' -Quiet | Should -BeTrue
    }
    It 'reads client-id as SecureString' {
        Select-String -Path $script:ScriptPath -Pattern 'SecureString' -Quiet | Should -BeTrue
    }
    It 'uses gh api to set variables' {
        Select-String -Path $script:ScriptPath -Pattern 'gh api' -Quiet | Should -BeTrue
    }
    It 'supports -Restore mode with snapshot file' {
        Select-String -Path $script:ScriptPath -Pattern '\$Restore' -Quiet | Should -BeTrue
        Select-String -Path $script:ScriptPath -Pattern '\$SnapshotPath' -Quiet | Should -BeTrue
    }
}
