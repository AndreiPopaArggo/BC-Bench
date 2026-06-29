# [Bug][SubscriptionBilling] Fix "Qty. to Invoice" incorrectly set on subscription item after partial shipment

<!-- Thank you for submitting a Pull Request. If you're new to contributing to BCApps please read our pull request guideline below
* https://github.com/microsoft/BCApps/Contributing.md
-->
#### Summary <!-- Provide a general summary of your changes -->
This pull request improves the handling of the "Qty. to Invoice" field for subscription items on sales documents, ensuring that it remains correctly set to zero after partial shipments. It also adds a new automated test to verify this behavior, preventing potential invoicing errors for subscription items.

#### Work Item(s) <!-- Add the issue number here after the #. The issue needs to be open and approved. Submitting PRs with no linked issues or unapproved issues is highly discouraged. -->
Fixes #6319



Fixes [AB#624268](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/624268)

