# [Subscription Billing]Subscription Lines Deletion Fix

<!-- Thank you for submitting a Pull Request. If you're new to contributing to BCApps please read our pull request guideline below
* https://github.com/microsoft/BCApps/Contributing.md
-->
#### Summary <!-- Provide a general summary of your changes -->
This pull request introduces improvements to the deletion logic for subscription headers and adds comprehensive tests to ensure correct handling of associated subscription lines. The main focus is to ensure that unassigned subscription lines are deleted when their header is deleted, while headers with assigned lines are protected from deletion.

### Deletion logic improvements

* Added a missing `SetRange("Subscription Contract No.")` filter before deleting service commitments in `table 8057 "Subscription Header"` to ensure only relevant records are deleted.

### Test coverage enhancements

* Added a test to verify that unassigned subscription lines are deleted when their subscription header is deleted in `codeunit 148157 "Service Object Test"`.
* Added a test to ensure an error is raised when attempting to delete a subscription header with subscription lines assigned to a contract, protecting data integrity.

#### Work Item(s) <!-- Add the issue number here after the #. The issue needs to be open and approved. Submitting PRs with no linked issues or unapproved issues is highly discouraged. -->
Fixes #6314




Fixes [AB#620365](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/620365)

