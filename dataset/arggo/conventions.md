# AL Coding Conventions

Policy snapshot v1.0 (2026-08-05). Reviews must enforce these rules in addition to general AL quality.

## Naming (ARGGO.NAMING.*)

- `PARAM_PREFIX` — procedure parameters use the `p` prefix: `pCustomerNo`, `pSalesHeader`.
- `LOCAL_PREFIX` — local variables use the `_` prefix: `_Customer`, `_totalAmount`.
- `GLOBAL_NO_PREFIX` — object-level (global) variables get **no** prefix.
- `TEMP_PREFIX` — temporary record variables carry `Temp`: `Temp_SalesLine`, `pTemp_SalesLine`.
- `RETURN_PREFIX` — named return values use the `r` prefix: `rBalance`. Use named returns for procedures that build up the result.
- `CASING` — object-type variables (Record, Codeunit, Page, ...) are Capitalized; primitive-type variables (Decimal, Boolean, Text, ...) are lowercase after their prefix.
- `DECL_ORDER` — `var` blocks declare complex/object types (Record, Codeunit, Page, ...) before simple types (AA0021).
- `NAME_LENGTH_30` — object and field names are capped at 30 characters **including** the mandatory affix; captions are not length-capped.

## Scope (ARGGO.SCOPE.*)

- `NARROWEST` — declare variables and Labels at the narrowest scope that uses them. Anything referenced by a single procedure belongs in that procedure's `var` block (with the `_` prefix), not at object level.

## Style (ARGGO.STYLE.*)

- `SELF_REFERENCE` — always call same-object procedures through `this.`.
- `INDENT_2SPACE` — 2-space indentation throughout.
- `NO_SINGLE_BEGIN_END` — no `begin..end` around a single statement (AA0005).

## Localization (ARGGO.LOC.*)

- `ERROR_LABELS` — every user-facing error message is a Label; use `TableCaption()` / `FieldCaption()` placeholders instead of hardcoded table or field names.
- `COMMENT_PLACEHOLDERS` — a Label/ToolTip/Caption `Comment` exists **only** to explain placeholders (`%1`, ...). Placeholders present → `Comment` required; none → no `Comment` (never a stub like `Comment = '%'`).
- `CAPTION_NO_AFFIX` — captions never include the mandatory affix; the affix lives in the object/field name only.
- `BLANK_CAPTION_LOCKED` — a blank caption (`Caption = ' '`) must carry `Locked = true` (AA0228); all other captions stay translatable.
- `TOOLTIP_TEMPLATE` — every page field gets a ToolTip. Fields mirroring a base-app concept reuse the base app's tooltip verbatim; custom fields use exactly `Specifies the value of the <field caption> field.`; actions get a short verb-first sentence.

## Performance (ARGGO.PERF.*)

- `SETLOADFIELDS` — call `SetLoadFields` before every `Get`/`FindFirst`/`FindSet`/`FindLast` on real tables read narrowly. Legitimate exceptions (do NOT flag these): the record feeds `TransferFields`; the record will be inserted, deleted, or renamed after the read, or copied to a temporary record; the variable is temporary; singleton setup-table reads; small bounded tables; reads that genuinely need every field; before `CalcSums`.
- `SETLOADFIELDS_ORDER` — order is `SetRange/SetFilter` → `SetLoadFields` → `SetAutoCalcFields` → `Find*`; a `SetLoadFields` placed before the filters is silently ignored.
- `SETUP_GETRECORDONCE` — setup tables read from multiple procedures use the `GetRecordOnce()` caching pattern instead of repeated raw `Get()` calls.
- `NO_UNNECESSARY_VALIDATE` — use `Validate` only when the `OnValidate` side effects are needed; otherwise assign directly.

## Records (ARGGO.PAT.*)

- `CHECKED_GET` — always check `Get`/`Find*` return values; never assume a record exists.
- `NO_COMMIT_IN_SUBSCRIBER` — never call `Commit()` inside an event subscriber.

## Project configuration (ARGGO.PROJ.*)

- `ID_RANGE` — new objects take IDs inside the ranges declared in the extension's `app.json`; never allocate IDs outside the declared ranges.

## Security (ARGGO.SEC.*)

- `DATA_CLASSIFICATION` — every table field declares an explicit `DataClassification`; `ToBeClassified` never ships; personal data is classified as `EndUserIdentifiableInformation`.
- `PERMISSION_SET` — every new object is covered by a permission set entry in the same change.
- `SECRET_TEXT` — credentials and tokens live in `SecretText` (Isolated Storage / Azure Key Vault); never plain `Text`, never hardcoded.
