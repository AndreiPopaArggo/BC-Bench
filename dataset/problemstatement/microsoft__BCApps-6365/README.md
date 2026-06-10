# Fix e-document draft UX: show error factbox and allow finalize from Ready for Draft state

- [x] Fix Error Messages FactBox visibility to show when there are errors/warnings
- [x] Update Finalize action visibility for both "Ready for Draft" and "Draft Ready" states
- [x] Remove extra reprocessing logic (per code review - underlying system handles this)
- [x] Add test verifying finalize from Ready for Draft state works correctly
- [x] Fix AA0175 linting error: use IsEmpty() instead of FindFirst() for existence check

## Summary of Changes

This PR fixes UX issues in the e-document draft page (Page 6181 "E-Document Purchase Draft"):

### Changes:

1. **Error Messages FactBox visibility** (line 275)
   - Changed from `Visible = false;` to `Visible = HasErrorsOrWarnings;`
   - Users can now see validation errors in the FactBox

2. **Finalize Action visibility** (line 527)
   - Extended to show for both "Ready for Draft" and "Draft Ready" states
   - The underlying system automatically runs the necessary steps

3. **Test added** (`EDocProcessTest.Codeunit.al`)
   - Added `FinishDraftFromReadyForDraftStateSucceeds` test
   - Verifies that finalize action from "Ready for Draft" state correctly processes to "Processed" state

<!-- START COPILOT CODING AGENT TIPS -->
---

≡ƒÆ¼ We'd love your input! Share your thoughts on Copilot coding agent in our [2 minute survey](https://gh.io/copilot-coding-agent-survey).




Fixes [AB#620054](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/620054)






