# Fix Trial Balance (Excel) Starting Balance date edge cases

## Summary
- Use period start date from the filter instead of deriving it from the first G/L Entry
- Wrap cutoff date in `ClosingDate()` so year-end closing entries are included in the Starting Balance
- Add tests for closing date and date boundary edge cases
- Set date filter in existing tests that were missing it

Fixes [AB#626498](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/626498)
Fixes #7143
