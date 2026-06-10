# Run-Comparison.ps1 - plugin-vs-vanilla matrix runner for the Arggo al-dev-toolkit evaluation.
#
# Conditions: vanilla  = instructions/skills/agents toggles OFF (stock agent)
#             plugin   = toggles ON (al-dev-toolkit profile: AGENTS.md + ALBugFix agent + skills)
# Agents:     claude (Claude Code), copilot (GitHub Copilot CLI)  [the only two under test]
# Modes:      run      = patch-only, no container needed (pipeline smoke / patch inspection)
#             evaluate = full scoring; requires Docker (Windows containers) + a prepared BC
#                        container per task (see RUNBOOK.md) + pwsh 7
#
# Examples:
#   .\Run-Comparison.ps1 -Agent claude -Condition plugin -Mode run -Model claude-haiku-4-5
#   .\Run-Comparison.ps1 -Agent claude -Condition vanilla -Mode evaluate -Model claude-sonnet-4-6 -Repeats 5
param(
    [ValidateSet('claude', 'copilot')] [string]$Agent = 'claude',
    [ValidateSet('vanilla', 'plugin')] [string]$Condition = 'vanilla',
    [ValidateSet('run', 'evaluate')] [string]$Mode = 'run',
    [string]$Model = 'claude-haiku-4-5',
    [string[]]$Tasks = @(),       # default: all 12 new public tasks
    [int]$Repeats = 1,
    [string]$RepoPath = "$env:USERPROFILE\bcbench-work\BCApps",
    [switch]$AlMcp                # add --al-mcp (AL MCP server lever)
)
$ErrorActionPreference = 'Stop'
$benchDir = Split-Path (Split-Path $PSScriptRoot)   # repo root (tools/arggo/..)
$configPath = Join-Path $benchDir 'src/bcbench/agent/shared/config.yaml'
$dataset = Join-Path $benchDir 'dataset/bcbench.jsonl'

if (-not $Tasks.Count) {
    $Tasks = @('microsoft__BCApps-7315', 'microsoft__BCApps-6636', 'microsoft__BCApps-7133',
        'microsoft__BCApps-7362', 'microsoft__BCApps-6237', 'microsoft__BCApps-6386',
        'microsoft__BCApps-6918', 'microsoft__BCApps-6365', 'microsoft__BCApps-5254',
        'microsoft__BCApps-4022', 'microsoft__BCApps-3277', 'microsoft__BCApps-3135')
}

# flip the experiment levers for the condition
$cfg = Get-Content $configPath -Raw
$enabled = if ($Condition -eq 'plugin') { 'true' } else { 'false' }
$cfg = $cfg -replace '(?s)(instructions:\s*\r?\n\s*enabled:\s*)(true|false)', "`${1}$enabled"
$cfg = $cfg -replace '(?s)(skills:\s*\r?\n\s*enabled:\s*)(true|false)', "`${1}$enabled"
$cfg = $cfg -replace '(?s)(agents:\s*\r?\n\s*enabled:\s*)(true|false)', "`${1}$enabled"
# IO.File writes UTF-8 WITHOUT BOM. PS 5.1's Set-Content -Encoding utf8 adds a BOM,
# which breaks the harness's YAML/Jinja loading (and Python JSON elsewhere).
[IO.File]::WriteAllText($configPath, $cfg)
"config: condition=$Condition (toggles=$enabled), agent entry=ALBugFix"

$entries = @{}
Get-Content $dataset | ForEach-Object { $o = $_ | ConvertFrom-Json; $entries[$o.instance_id] = $o }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outRoot = "$env:USERPROFILE\bcbench-work\results\$stamp-$Agent-$Condition-$Model"
New-Item -ItemType Directory -Force $outRoot | Out-Null

Set-Location $benchDir
foreach ($rep in 1..$Repeats) {
    foreach ($t in $Tasks) {
        $e = $entries[$t]
        if (-not $e) { Write-Warning "unknown task $t"; continue }
        "== [$rep/$Repeats] $t ($Agent/$Condition/$Model/$Mode) =="

        # reset the working repo to the task's base commit
        git -C $RepoPath sparse-checkout set --cone @($e.project_paths) 2>&1 | Out-Null
        git -C $RepoPath checkout --detach --force $e.base_commit 2>&1 | Out-Null
        git -C $RepoPath clean -fdx 2>&1 | Out-Null

        $outDir = Join-Path $outRoot "rep$rep"
        $args = @($Mode, $Agent, $t, '--category', 'bug-fix', '--model', $Model,
            '--repo-path', $RepoPath, '--output-dir', $outDir)
        if ($AlMcp) { $args += '--al-mcp' }
        uv run bcbench @args 2>&1 | Select-Object -Last 4
    }
}
""
"results under: $outRoot"
"aggregate with: uv run bcbench result summarize <run-dir>  (see bcbench result --help)"
