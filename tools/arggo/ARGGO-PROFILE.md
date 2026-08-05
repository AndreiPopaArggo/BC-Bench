# Arggo review profile

Makes "success" on the code-review category include Arggo conventions and best practices,
without touching upstream datasets or default scoring. Designed 2026-08-05 (Claude + Sol
consult); the design follows a profile-based architecture rather than an FP-exemption patch.

## What it is

`--review-profile arggo` on `bcbench evaluate copilot|claude` (code-review only; default
`upstream` is bit-for-bit unchanged — regression-tested in `tests/test_arggo_profile.py`).

Three data sources, all frozen in git (no live judge decides acceptability at scoring time):

| File | Contents |
|---|---|
| `dataset/arggo/codereview.jsonl` | 24 new entries: 12 defect/clean pairs (`metadata.pair_id`), golds = Arggo convention violations with `rule_id` (ARGGO.*), 50/50 split on `metadata.discoverability` — `workspace` entries commit a `CONVENTIONS.md` fixture into the repo before the review (visible context, excluded from the reviewed diff); `plugin` entries state conventions nowhere in-repo |
| `dataset/arggo/upstream-overlays.jsonl` | Per-upstream-entry annotations: `required_comments` (join golds; TP/FN) and `allowed_comments` (neutral: matching one is neither TP nor FP). An upstream entry **without** an overlay refuses to run under the profile — partially annotated aggregates are forbidden |
| `dataset/arggo/conventions.md` | Frozen policy snapshot v1.0 with rule IDs; also the CONVENTIONS.md fixture content |

Scoring changes (all additive, zero-effect when the new fields are empty):

- Matching order: generated ↔ golds first (structural + LLM judge), then leftover generated ↔
  `allowed_comments` (structural + judge). Everything still unmatched is FP; unmatched golds are FN.
- Precision = matched / (generated − allowed_matched); recall untouched. One-to-one matching
  caps neutralization at the annotation cardinality — duplicate/spam findings stay FPs.
- New reported metrics: `allowed_match_count`, `clean_task_count`, `clean_pass_rate`,
  `mean_fp_per_clean_task`. Report the three outcomes separately, never blended:
  (1) upstream score on the untouched upstream profile, (2) Arggo conformance on the
  `arggo__` slice, (3) the over-enforcement gate.
- The arggo profile appends one neutral prompt line pointing agents at `CONVENTIONS.md`
  (same line for every arm and entry, so discoverability is a property of the workspace,
  not the prompt).

## v1 overlay policy (2026-08-05)

`upstream-overlays.jsonl` is **allowed-only**: `required_comments` are empty pending human
adjudication. Allowed candidates were mined from the 2026-08-04 arm-D pilot findings via
rule classifiers (`~/bcbench-work/arggo-tasks/curate_overlays.py`), with deliberate
exclusions: SetLoadFields advice on setup-table reads stays FP (al-performance scopes that
as an exception). Consequences: the overlaid upstream slice grants no house-rule recall
credit (the `arggo__` set carries the recall signal), and acceptance bias toward arm-D's
own phrasing is documented — independent adjudication + promotion to `required` is the
planned hardening step before any headline claim.

## Claim discipline (Sol)

The `arggo__` golds are authored from the plugin's own skill docs. The numbers therefore
support a **policy-delivery/conformance** claim ("the plugin delivers Arggo conventions the
base agent doesn't apply, without regressing upstream defect detection or clean-task
noise"), NOT a general review-intelligence claim. Known confound: arm D changes model +
prompt + tools at once; a same-Luna-no-plugin ablation arm is the planned control.

## Running the battery

Workspace scripts (outside the repo, `~/bcbench-work/`):

- `arggo-runner.ps1` — arms a (baseline auto) and d (`--agent=al-dev-toolkit:code-reviewer`)
  over 24 `arggo__` + 18 overlaid upstream entries, all `--review-profile arggo`; resumable
  via `arm-results/progress-arggo.jsonl`. Run OUTSIDE any tool sandbox.
- `aggregate-arggo.ps1` — per-arm slice report (arggo/upstream/documented/plugin splits).
- Entry sources + generator: `~/bcbench-work/arggo-tasks/` (`generate_entries.py` rebuilds
  `dataset/arggo/codereview.jsonl` from per-entry manifests; anchors golds by unique
  substring so line numbers cannot drift).

Statistical note: 12 pairs ≈ smoke-test scale. Minimum for a stable headline: ~3 runs/arm,
bootstrap by pair_id; expand toward 16-20 pairs before publishing numbers.
