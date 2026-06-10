# Fix eDocument PEPPOL BIS 3.0 import errors for text-only document references and hierarchical line IDs

## Summary

- Fix "Please choose a file to attach" error when importing PEPPOL invoices/credit memos with `AdditionalDocumentReference` elements that have no `<cac:Attachment>` child (text-only references). Added `"File Name" <> ''` guard to all 4 attachment insert locations.
- Fix "The value '1.1' can't be evaluated into type Integer" error when importing documents with hierarchical line numbering (e.g., 1.1, 1.2). Replaced direct `Evaluate` of XML line ID with auto-incrementing counter (10000, 20000, ...) passed as `var` parameter from caller to parser.
- Added test XML fixtures and automated tests in `EDocumentStructuredTests`.

[AB#626739](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/626739)




