# Dynamics 365 Business Central (AL) Development — al-dev-toolkit profile

Dynamics 365 Business Central is Microsoft's cloud-based ERP solution for small and medium-sized businesses, covering finance, supply chain, sales, inventory, manufacturing, and service management.

**AL (Application Language)** is a domain specific programming language for Business Central development:
- Each AL project is defined by an `app.json` file at its root folder
- Apps are compiled into `.app` packages for deployment
- Object types: Tables, Pages, Codeunits, Reports, Queries, XMLports, etc.
- Extensibility through events and object (table/page/enum) extensions

## Working discipline (al-dev-toolkit)

Follow this sequence on every task. Do not skip steps.

1. **Understand before touching.** Restate the issue in one line: which action, which object/area, what wrong outcome. Identify the involved objects from the issue text and any screenshots.
2. **Locate semantically first.** When AL tools are available, prefer symbol queries over file reads: `al_symbolsearch` to find objects/procedures, `al_symbolrelations` to answer "who extends / implements / uses X". Otherwise use targeted greps for object names, field names, and error-message text. Read only the files on the failing code path.
3. **Diagnose the root cause, not the symptom.** Trace the wrong behavior to a specific procedure and line. State the root cause to yourself before editing. Never guess an event signature, field type, or procedure name — verify it exists in this codebase first.
4. **Fix with a minimal surgical diff.** Touch only the lines that cause the issue. No refactoring, no renames, no drive-by "improvements", no new objects unless unavoidable. If a new object is unavoidable: name <= 30 chars, ID within the project's `app.json` idRanges and unused.
5. **Match the surrounding style exactly.** This repository follows Microsoft base-app conventions. Mirror the file you are editing: its naming, casing, comment density, and patterns. Code samples inside skills illustrate *principles* — they are not naming rules for this repo.
6. **Verify.** When build tools are available (`al_build` / `al_compile` + `al_getdiagnostics`): build, then fix diagnostics **one at a time**, rebuilding after each fix, until the touched files are clean. When build tools are NOT available, do a strict mental compile instead: every procedure, field, enum value, and library you reference must exist in this codebase (search for it), parameter counts and types must match, and the edit must be syntactically complete.
7. **Self-review before finishing** (the toolkit's reviewer gate, applied to your own diff):
   - Does the diff actually fix the reported issue, including the edge cases named in the issue?
   - Bug-fix tasks: zero changes to test files or test logic.
   - No unintended behavior change for other callers of the touched code (check who calls the procedure you changed).
   - No new diagnostics introduced; W1 localization only.
   - Nothing in the diff that the issue did not require.
   If a check fails, fix it and re-verify. Then stop — do not continue past a passing review.

## Skills

Detailed reference lives in skills (auto-discovered): `al-performance` (SetLoadFields, FlowFields, set-based ops, caching), `al-patterns` (events, IsHandled, temp tables, TryFunction, dedup guards), `al-diagnostics` (compiler/CodeCop/AppSourceCop error codes and their standard fixes). Consult them when the work touches their domain; do not paste them wholesale into your reasoning.

## Hard constraints

- Do NOT modify test files or testing logic on bug-fix tasks.
- Do NOT commit anything.
- Focus on W1 — ignore other localizations (DK, APAC, ...).
- Do NOT invent symbols: if you cannot find a procedure/field you believe should exist, search for the actual API before using it.
