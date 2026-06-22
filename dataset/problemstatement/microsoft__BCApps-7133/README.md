# Fix TestManual throws "No. Series does not exist" error for blank code

<!-- Thank you for submitting a Pull Request. If you're new to contributing to BCApps please read our pull request guideline below
* https://github.com/microsoft/BCApps/Contributing.md
-->
#### Summary <!-- Provide a general summary of your changes -->
Summary
When users create a Vendor (or other cards like Bank Account) without configuring a Number Series in the Setup page and try to enter a manual number, the system throws the error: "The No. Series does not exist. Identification fields and values: Code=''"

The API documentation states this function "allows manual numbers for blank No. Series Codes", but the implementation does not handle blank codes.


#### Work Item(s) <!-- Add the issue number here after the #. The issue needs to be open and approved. Submitting PRs with no linked issues or unapproved issues is highly discouraged. -->
Fixes [AB#625540](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/625540)




