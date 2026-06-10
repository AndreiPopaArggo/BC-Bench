---
name: al-patterns
description: AL design patterns — integration events and IsHandled, event subscribers, interfaces, temporary tables, TryFunction, GuiAllowed, dedup guards, CommitBehavior. Use when changing extensibility points or designing AL logic.
---

# AL Design Patterns

Samples use Microsoft base-app naming — always match the conventions of the file you are editing.

## Events for extensibility

Prefer events over direct modification. Standard publisher shape:

```al
[IntegrationEvent(false, false)]
local procedure OnBeforePostDocument(var SalesHeader: Record "Sales Header"; var IsHandled: Boolean)
begin
end;

procedure PostDocument(var SalesHeader: Record "Sales Header")
var
    IsHandled: Boolean;
begin
    OnBeforePostDocument(SalesHeader, IsHandled);
    if IsHandled then
        exit;
    // default implementation
    OnAfterPostDocument(SalesHeader);
end;
```

**Rules:**
- `IsHandled` pattern for overridable behavior; check it immediately after raising the event.
- **Never `Commit()` inside an event subscriber.**
- A subscriber's `[EventSubscriber]` attribute must name the event **exactly** (OnBefore vs OnAfter typos are real bugs — verify against the publisher's declaration, never guess).
- The attribute's 4th parameter (element/field name) must match the publisher's element exactly when subscribing to field-level events.

## Interfaces

`interface "IName" { procedure ...; }` + `codeunit X "Impl" implements "IName"`. When fixing code that dispatches via an interface, find the relevant implementation codeunit(s) with who-implements queries rather than assuming.

## Temporary tables

Use temp records to buffer multi-pass processing and avoid DB writes mid-computation. A `temporary` record never writes to the database — passing one where a real record is expected (or vice versa) is a classic bug source; check the `temporary` keyword on both sides.

## TryFunction

`[TryFunction]` procedures convert runtime errors into a `false` return; read the error with `GetLastErrorText()`. Inside a TryFunction, do not write to the database (writes are rolled back in ways that surprise callers).

## CommitBehavior

`[CommitBehavior(CommitBehavior::Ignore)]` on wrappers suppresses implicit commits (used by posting-preview flows). If a fix touches posting/preview paths, preserve the existing CommitBehavior semantics.

## GuiAllowed

Wrap Dialog/Window/Message/Confirm in `if GuiAllowed() then` when the code can run from job queue, API, or web-service sessions — a Confirm in a non-UI session throws.

## Deduplication guard

Loops over data with repeated keys: sorted → compare against a LastSeen variable; unsorted → `Dictionary of [Code[20], Boolean]` membership check before processing.

## Setup-table read caching

Single-record setup tables expose `GetRecordOnce()` (a `RecordHasBeenRead` flag + `Get()`); callers in loops/posting use it instead of raw `Get()`.
