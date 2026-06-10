---
name: al-performance
description: AL database performance rules — SetLoadFields, FindSet vs Get, set-based operations, FlowField handling, caching, avoiding unnecessary Validate. Use when writing or reviewing AL code that reads from the database.
---

# AL Performance Guidelines

Samples use Microsoft base-app naming — always match the conventions of the file you are editing.

## SetLoadFields (partial records)

Use `SetLoadFields` before `Get` / `FindFirst` / `FindSet` / `FindLast` to load only needed columns.

**Skip it when:** the record is passed to `TransferFields` (needs every field), you genuinely need all fields, or before `CalcSums`.

**Order matters: SetRange → SetLoadFields → SetAutoCalcFields → Find.** A `SetLoadFields` placed before `SetRange` is silently ignored.

```al
Item.SetRange("Item Category Code", CategoryCode);
Item.SetLoadFields(Description);
if Item.FindSet() then
    repeat
        // use Item.Description
    until Item.Next() = 0;
```

## FindSet vs FindFirst vs Get

| Method | Use case |
|--------|----------|
| `Get()` | Exact primary-key lookup |
| `FindFirst()` | Single record with filters |
| `FindSet()` | Looping with repeat..until |
| `IsEmpty()` | Existence check only — cheaper than FindFirst |

## Set-based operations

Prefer `CalcSums` over manual aggregation loops; `ModifyAll`/`DeleteAll` over loop + individual `Modify`/`Delete`.

```al
CustLedgerEntry.SetRange("Customer No.", CustomerNo);
CustLedgerEntry.CalcSums(Amount);
TotalAmount := CustLedgerEntry.Amount;
```

## FlowFields

- Never filter on a FlowField (`SetFilter(Balance, ...)` forces calculation for every record).
- FlowField needed for most/all loop records → `SetAutoCalcFields` before Find (single join).
- FlowField needed for a small subset → `CalcFields` inside an `if` guard in the loop.
- Never include FlowFields in `SetLoadFields`.

## Caching

- Repeated lookups by the same key inside loops → Dictionary cache or temp-table buffer.
- Setup tables read repeatedly across procedures → a `GetRecordOnce()` procedure with a `RecordHasBeenRead` flag on the table (BC base-app pattern) instead of raw `Get()` per caller.
- Loops over sorted data with repeated keys → last-seen guard variable; unsorted → Dictionary dedup.

## Avoid unnecessary Validate

`Validate` runs OnValidate triggers and their subscribers. Use it only when those side effects are wanted (e.g. `Validate("No.", ItemNo)` to trigger defaulting). For plain assignments — especially batch/migration code — use `:=`.

## BLOB / Media in bulk reads

Never include BLOB, Media, or MediaSet fields in `SetLoadFields` or query columns during bulk processing; load them individually behind a need check.

## Checklist

- [ ] SetLoadFields before every Get/Find (except TransferFields feeds / CalcSums)
- [ ] SetLoadFields after SetRange, before Find
- [ ] No FlowFields in SetFilter/SetRange; SetAutoCalcFields for loop-wide FlowFields
- [ ] FindSet for loops, Get for PK, IsEmpty for existence
- [ ] CalcSums / ModifyAll / DeleteAll over loops
- [ ] No DB reads inside tight loops (cache instead)
- [ ] Validate only for wanted side effects
