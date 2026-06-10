# Arggo al-dev-toolkit evaluation runbook

Branch `arggo/al-dev-toolkit-eval` of the BC-Bench clone. Goal: measure how much the
al-dev-toolkit plugin profile raises bug-fix solve rates for **Claude Code** and
**GitHub Copilot CLI** (the only two agents BC-Bench supports).

## What this branch adds

1. **12 new verified public tasks** (dataset 4 -> 16 public BCApps entries), mined from
   merged BCApps fix-PRs and individually verified: patches apply at `base_commit`,
   FAIL_TO_PASS functions exist as added `[Test]` procedures, statements reviewed.
   Curation: 6727 dropped (collector missed a third project); 6636/6386 F2P trimmed of
   exact-error-label-coupled tests; 6636 statement enriched with public issue #6281.
   `environment_setup_version` is mapped from the merge month and is **provisional until
   a container build confirms it** (adjust if `Invoke-AppBuildAndPublish` fails on version).
   System-layer entries (7133 Business Foundation; 4022/3277/3135 System Application;
   5254 touches System Application tests) may build slow/heavy in containers - validate
   before counting them in headline numbers.
2. **The plugin profile** under `src/bcbench/agent/shared/instructions/microsoft-BCApps/`:
   `AGENTS.md` (toolkit working discipline -> becomes CLAUDE.md / copilot-instructions.md),
   `agents/ALBugFix.agent.md` (entry agent: locate -> diagnose -> minimal fix -> verify ->
   self-review), skills `al-performance`, `al-patterns`, `al-diagnostics`.
   Arggo-project conventions (prefixes, affixes, ID ranges) are deliberately excluded -
   BCApps follows Microsoft style; we measure the *workflow + BC knowledge* transfer.
3. **`tools/arggo/Run-Comparison.ps1`** - the matrix runner (flips config.yaml toggles,
   resets the repo per task, invokes bcbench).

## Prerequisites

| Item | Status on the dev laptop (2026-06-10) |
|---|---|
| Python 3.13 via uv (`uv sync`) | done |
| Claude Code CLI (`claude`) | installed, subscription auth |
| Copilot CLI 1.0.57 | installed at `~/.npm-global/copilot.cmd` (npm registry is network-blocked; installed from tarball). Needs `copilot` on PATH + GitHub auth (`COPILOT_GITHUB_TOKEN` or interactive login) before first run. |
| pwsh 7 | installed via `dotnet tool install --global PowerShell` |
| Docker (Windows containers) | **NOT running** - start Docker Desktop, switch to Windows containers. Required only for `evaluate` (scoring). |
| BCApps working clone | `~/bcbench-work/BCApps` (partial clone; runner resets it per task) |

## Conditions

- **vanilla**: `instructions/skills/agents` toggles all `false` -> stock agent.
- **plugin**: all `true` + `--agent=ALBugFix` -> al-dev-toolkit profile.
- Optional extra lever: `-AlMcp` adds Microsoft's AL MCP server (compare against the
  leaderboard's +4.4pp altool result).

## Suggested matrix (per BC-Bench's EXPERIMENT.md ramp)

1. Patch-only smoke (no container): `.\Run-Comparison.ps1 -Agent claude -Condition plugin -Mode run -Tasks microsoft__BCApps-7133`
2. Full eval, W1-app tasks first, both conditions:
   - `.\Run-Comparison.ps1 -Agent claude -Condition vanilla -Mode evaluate -Model claude-sonnet-4-6 -Repeats 5`
   - `.\Run-Comparison.ps1 -Agent claude -Condition plugin  -Mode evaluate -Model claude-sonnet-4-6 -Repeats 5`
   - same for `-Model claude-haiku-4-5`, then `-Agent copilot` (model id dot-form: `claude-sonnet-4.6`).
3. Report: solve rate (resolved/total) per condition + delta, mean tokens and duration
   per task (Claude Code is context-heavy; expect the plugin profile to add input tokens -
   the question is whether solve-rate gains justify it). Use `bcbench result` to summarize;
   results across different `benchmark_version`s must not be aggregated.

## Container setup for `evaluate` (per task)

BC-Bench's CI creates one container per task via
`scripts/Setup-ContainerAndRepository.ps1` (BcContainerHelper, `Get-BCArtifactUrl
-version <environment_setup_version> -Country w1`). Locally: ensure Docker is in Windows-
container mode, `Install-Module BcContainerHelper`, and either reuse that script or
pre-create a container matching the task's BC version, then pass `--container-name`
(or env `BC_CONTAINER_NAME`, with `BC_SERVER_USERNAME`/`BC_SERVER_PASSWORD`).
Container BC version MUST match the entry's `environment_setup_version` or compilation
fails confusingly (community-reported gotcha).

## Open items

- CentralGauge import is **blocked on licensing** (README declares MIT but the repo has
  no LICENSE file) and structure (write-from-spec; no gold patch, no buggy baseline).
  If wanted: ask the author (Torben Leth / SShadowS) to add the LICENSE, then clean-room
  convert the top candidates (H001 tax calculator, H004 enum-ordinal trap, H021 interface
  collections, M010 multi-object, H205 event-spy) by authoring solutions + injected bugs.
- Validate provisional `environment_setup_version` values with one container build per
  version (27.2, 27.4, 27.5, 28.0, 26.2, 25.5).
- Copilot CLI auth + a Copilot-side smoke run.
