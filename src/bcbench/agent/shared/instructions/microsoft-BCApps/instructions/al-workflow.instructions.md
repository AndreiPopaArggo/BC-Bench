---
description: "Route AL work through al-dev-toolkit. Applied automatically when an AL file is in context."
applyTo: "**/*.al"
---

# AL Workflow Guard

This project uses the al-dev-toolkit plugin. AL edits must go through its commands — the plugin owns the conventions, patterns, performance, and security rules.

## Routing

<!-- SYNC: the canonical routing map lives in the plugin's session-start hook (hooks/session-start-plugin-skills.ps1) - update both together -->

| Request | Command |
|---|---|
| Implement an arggoplanner task end-to-end | `/do-task <taskID>` |
| Vague idea, not sure what to build | `/brainstorming` → `/al-planning` |
| New objects, multi-object change, new feature, event subscriptions | `/al-planning` → `/al-implementation` |
| 1-2 file change (field, property, caption, page tweak) | `/quick` |
| Compiler error | `/build-fix` |
| Run AL tests / check they pass (BC 28.0+) | `/al-test` |
| Review changed files | `/code-review-al` |
| Review the whole project | `/project-code-review` |
| BC base app question (events, tables, procedures) | `/bc-research` |
| Generate project documentation | `/generate-project-docs` |
| Which command do I use? / plugin help | `/al-help` |

Do NOT edit AL directly without running one of these commands. Multi-object work must start with `/al-planning` — the plan is the contract the coder agent implements against.

## Skill enforcement

When editing AL through any of the commands above, the agent must load and apply the plugin's AL skill library:

- `al-coding-style` — naming, declaration order, Labels, self-reference
- `al-patterns` — events, interfaces, temp tables, setup tables
- `al-performance` — SetLoadFields, FindSet vs Get, FlowField handling
- `al-security` — DataClassification, permission sets, credential handling

The `coder` agent preloads these automatically. Any other agent editing AL must load them explicitly before writing code.

## Base-app references

When reading Microsoft base-app code via `arggo-bc-symbols` or `microsoft-learn` MCPs, use it for signatures, behavior, and patterns only. Do **not** copy variable names verbatim — Microsoft base app uses different conventions (no `_` on locals, no `p` on parameters, etc.). The project conventions in `al-coding-style` apply to every variable you declare, regardless of what surrounding lookup results look like.
