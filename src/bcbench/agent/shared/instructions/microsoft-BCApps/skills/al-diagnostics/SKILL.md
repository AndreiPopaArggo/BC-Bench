---
name: al-diagnostics
description: AL compiler, CodeCop, and AppSourceCop diagnostic codes with their standard fixes, plus the build-fix discipline (one error at a time, symbols before code changes).
---

# AL Diagnostics Reference

## Build-fix discipline

1. Fix in priority order: **AL0xxx (compiler) → dependency/symbol issues → AA0xxx (CodeCop) → AS0xxx (AppSourceCop)**.
2. **One error at a time**, recheck diagnostics after each fix — cascading errors often disappear, and the list is usually shorter than expected.
3. Only touch the lines that cause errors. Never refactor while fixing. Never change business logic to silence a type error.
4. Max 3 attempts per individual error; if it does not resolve, reconsider the diagnosis instead of retrying variations.

## Missing-symbol errors come first

Before editing code for a missing-object / not-accessible error (AL0185 and friends), check whether symbols are simply absent — this is often **not** a code bug:
1. Download/restore symbols if a symbol tool is available; rebuild — the error often clears with zero code change.
2. If the object lives in an app not referenced yet, the dependency belongs in `app.json` `dependencies`.
3. Only after symbols are confirmed present, treat it as a code issue (typo, wrong `Access`, wrong namespace/`using`).

## Common AL compiler errors (AL0xxx)

| Code | Issue | Fix |
|------|-------|-----|
| AL0118 | Name not in context | Declare the variable / check spelling and `using` namespaces |
| AL0132 | Duplicate member name | Use a unique name |
| AL0185 | Object not accessible / symbol missing | Symbols first (see above), then app.json deps / Access |
| AL0217 | Invalid property value | Use a valid value (e.g. DataClassification enum) |
| AL0254 | Record not initialized | Add Get/Find before use |
| AL0432 | Object ID outside range | Check app.json idRanges |
| AL0499 | Cannot convert type | Use Evaluate() or the correct type |
| AL0603 | Return type mismatch | Return the declared type |
| AL0896 | FlowField recursively dependent | Break the FlowField dependency cycle |
| AL0910/AL0911 | Empty field/key name; FlowField/FlowFilter in Query DataItemLink | Provide names; don't link on FlowFields |
| AL0916 | Ambiguous built-in overload on a Variant argument | Cast/Evaluate the argument to the intended type |

## Common CodeCop warnings (AA0xxx)

| Code | Issue | Fix |
|------|-------|-----|
| AA0001 | Implicit `with` | Explicit record variable reference |
| AA0005 | Unnecessary `begin..end` | Remove around single statements |
| AA0008 | Missing parentheses | Add `()` to method calls |
| AA0021 | Variable declaration order | Object types before simple types: Record → Report → Codeunit → XmlPort → Page → Query → Notification → BigText → DateFormula → RecordId → RecordRef → FieldRef → then Text/Code/Integer/... |
| AA0074 | Exit not last statement | Restructure control flow |
| AA0137 | Unused variable | Remove the declaration |
| AA0139 | Possible overflow / TextConst obsolete | Use Label; size Text/Code correctly |
| AA0175 | Find('-')/Find('+') | Use FindFirst()/FindLast() |
| AA0181 | FindFirst/FindLast used for looping | Use FindSet() with repeat..until |
| AA0228 | Blank caption not locked | `Caption = ' ', Locked = true` |

## Common AppSourceCop errors (AS0xxx)

| Code | Issue | Fix |
|------|-------|-----|
| AS0011 | ID outside assigned range | Use the assigned range |
| AS0013 | Removed public member | ObsoleteState + ObsoleteTag instead of deleting |
| AS0018 | Obsolete without reason | Add ObsoleteReason |

## Reading diagnostics

Prefer structured diagnostics (the `al_getdiagnostics` tool) over parsing build text: it returns file, line, column, code, severity, and message per finding. Treat warnings on files you touched as must-fix unless an existing pragma/ruleset explicitly accepts them.
