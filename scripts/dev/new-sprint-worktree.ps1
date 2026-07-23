<#
.SYNOPSIS
    Create an isolated worktree + short-lived branch for a parallel sprint, off main.

.DESCRIPTION
    Implements the trunk-based, worktree-per-sprint model from ADR-0038 and
    docs/DEV_WORKFLOW.md: main is the baseline of truth, and each parallel sprint
    or task runs in its own git worktree with its own Copilot CLI session.
    Branches are short-lived and ALWAYS based on the latest origin/main
    (never stacked on another feature branch).

.PARAMETER Sprint
    Sprint number, e.g. 30.

.PARAMETER Topic
    Short topic slug for the branch and worktree, e.g. forecast.

.PARAMETER BaseBranch
    Base branch to fork from. Defaults to main.

.EXAMPLE
    ./scripts/dev/new-sprint-worktree.ps1 -Sprint 30 -Topic forecast
    Creates ../wt/sprint-30-forecast on branch sprint-30/forecast off origin/main.
#>
param(
    [Parameter(Mandatory = $true)][int]$Sprint,
    [Parameter(Mandatory = $true)][string]$Topic,
    [string]$BaseBranch = 'main'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$slug = ($Topic.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if ([string]::IsNullOrWhiteSpace($slug)) { throw "Topic '$Topic' produced an empty slug." }

$branch = "sprint-$Sprint/$slug"
$repo = (git rev-parse --show-toplevel).Trim()
$wtRoot = Join-Path (Split-Path $repo -Parent) 'wt'
$wtPath = Join-Path $wtRoot "sprint-$Sprint-$slug"

if (Test-Path $wtPath) { throw "Worktree path already exists: $wtPath" }

Write-Host "Fetching latest origin/$BaseBranch ..." -ForegroundColor Cyan
git fetch origin $BaseBranch

New-Item -ItemType Directory -Force -Path $wtRoot | Out-Null

Write-Host "Creating worktree on new branch '$branch' (off origin/$BaseBranch) ..." -ForegroundColor Cyan
git worktree add -b $branch $wtPath "origin/$BaseBranch"

Write-Host ""
Write-Host "Worktree ready." -ForegroundColor Green
Write-Host "  Path   : $wtPath"
Write-Host "  Branch : $branch"
Write-Host ""
Write-Host "Start an independent Copilot CLI session for this sprint:" -ForegroundColor Yellow
Write-Host "  cd `"$wtPath`""
Write-Host "  copilot --allow-all-tools"
Write-Host ""
Write-Host "After the sprint's pull request is squash-merged, clean up:" -ForegroundColor Yellow
Write-Host "  git worktree remove `"$wtPath`""
Write-Host "  git branch -D $branch"
Write-Host "  git push origin --delete $branch"
