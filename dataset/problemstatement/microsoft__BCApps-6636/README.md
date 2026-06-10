# [Subscription Billing] Fix deferral creation, release, and credit memo handling

<!-- Thank you for submitting a Pull Request. If you're new to contributing to BCApps please read our pull request guideline below
* https://github.com/microsoft/BCApps/Contributing.md
-->
#### Summary <!-- Provide a general summary of your changes -->
This pull request introduces a new data upgrade step to populate posting group fields in contract deferral records, along with some code clean-up and improvements/fixes across related modules. 
1. **Extensibility**: Five core deferral objects need integration points (events) for ISV extensions to customize behavior during deferral creation and release processes.

2. **Missing Posting Groups in Deferrals**: Contract deferrals cannot be released when the original posted documents are unavailable (e.g., in data migration scenarios), because posting group information is retrieved from posted invoice/credit memo lines instead of being stored in the deferral entries.

3. **Zero-Amount Deferrals**: The system creates unnecessary deferral entries and G/L postings for contract lines with 0.00 amounts, leading to excessive ledger entries with no financial impact.

4. **Inconsistent Partial Period Handling**: Vendor contract deferrals handle partial billing periods inconsistently—some invoices are deferred based on full months while others are calculated daily, causing incorrect revenue recognition.

5. **Credit Memo Deferral Gap**: Credit memos with amounts exceeding the original invoice amount do not generate corresponding deferral entries, resulting in incomplete revenue recognition.

6. **Double Deferral Generation**: When both contract-based deferrals and standard deferral codes are used, deferrals are incorrectly created in both systems simultaneously.


#### Work Item(s) <!-- Add the issue number here after the #. The issue needs to be open and approved. Submitting PRs with no linked issues or unapproved issues is highly discouraged. -->
Fixes #6281
[AB#623188](https://dynamicssmb2.visualstudio.com/1fcb79e7-ab07-432a-a3c6-6cf5a88ba4a5/_workitems/edit/623188)














---

## Linked issue #6281: [Bug][Extensibility][MultiObjects][Subscription Billing] Deferrals extensibility and multiple critical fixes

### Describe the issue

This issue addresses multiple critical bugs and extensibility gaps in the Microsoft Subscription Billing deferrals functionality. The current implementation has the following issues:

1. **Extensibility**: Five core deferral objects need integration points (events) for ISV extensions to customize behavior during deferral creation and release processes.

2. **Missing Posting Groups in Deferrals**: Contract deferrals cannot be released when the original posted documents are unavailable (e.g., in data migration scenarios), because posting group information is retrieved from posted invoice/credit memo lines instead of being stored in the deferral entries.

3. **Zero-Amount Deferrals**: The system creates unnecessary deferral entries and G/L postings for contract lines with 0.00 amounts, leading to excessive ledger entries with no financial impact.

4. **Inconsistent Partial Period Handling**: Vendor contract deferrals handle partial billing periods inconsistently—some invoices are deferred based on full months while others are calculated daily, causing incorrect revenue recognition.

5. **Credit Memo Deferral Gap**: Credit memos with amounts exceeding the original invoice amount do not generate corresponding deferral entries, resulting in incomplete revenue recognition.

6. **Double Deferral Generation**: When both contract-based deferrals and standard deferral codes are used, deferrals are incorrectly created in both systems simultaneously.





### Expected behavior


### Extensibility Enhancements

**Objects requiring extensibility events:**
- Report 8051 "Contract Deferrals Release"
- Table 8066 "Cust. Sub. Contract Deferral"
- Table 8072 "Vend. Sub. Contract Deferral"
- Report 8052 "Cust. Contr. Def. Analysis"
- Report 8053 "Vend Contr. Def. Analysis"

**Required events:**
1. **OnBeforeInsertGenJournalLine** event in ReleaseContractDeferral/related functions to allow ISVs to skip journal line insertion based on custom logic
2. **OnAfterInitFromSalesLine** event in InitFromSalesLine procedure
3. **OnAfterInitFromPurchaseLine** event in InitFromPurchaseLine procedure

### Bug Fixes Expected Behavior

**Task 2 - Posting Groups Storage:**
- Add "Gen. Bus. Posting Group" and "Gen. Prod. Posting Group" fields to both deferral tables
- Populate these fields during deferral entry creation from the invoice line
- Modify release logic to use stored posting groups instead of retrieving from posted documents
- Implement data upgrade to retrospectively fill posting groups from existing document lines

**Task 3 - Zero-Amount Prevention:**
- Skip deferral entry creation when the deferral amount equals 0.00
- Prevent G/L postings for zero-amount deferrals during release
- Reduce unnecessary ledger entries significantly in contracts with multiple zero-amount lines

**Task 4 - Consistent Partial Period Calculation:**
- Apply consistent day-based calculation for all partial billing periods in vendor contracts
- Ensure both the first and last month of multi-month periods are calculated proportionally based on actual days
- Monthly amounts should match deferral amounts when billing covers full calendar months

**Task 5 - Credit Memo Deferral Handling:**
- Generate negative deferral entries for all credit memos, regardless of amount
- Ensure credit memos that exceed original invoice amounts create corresponding deferral adjustments
- Maintain complete and accurate deferral schedules reflecting all revenue adjustments

**Task 6 - Prevent Double Deferrals:**
- Block "Deferral Code" field on Sales Line and Purchase Line when contract deferrals are enabled
- Field should only be editable when:
  - Contract line has "Create Contract Deferrals" = No, OR
  - Contract line has "Create Contract Deferrals" = Contract-dependent AND contract header has "Create Contract Deferrals" = No

### Steps to reproduce

### Task 2 - Missing Posting Groups
1. Import contract deferral data from legacy system (without corresponding posted documents)
2. Navigate to Contract Deferrals Release (Report 8051)
3. Set posting date and post-until date
4. Execute release process
5. **Result**: Error occurs because system cannot retrieve posting groups from non-existent posted invoice lines

### Task 3 - Zero-Amount Deferrals
1. Create a Customer Subscription Contract with 11 lines:
   - 1 line with monthly amount (e.g., €100)
   - 10 lines with 0.00 amount (asset subscriptions)
2. Enable "Contract Deferrals" = Yes
3. Create and post contract invoice
4. Execute Contract Deferral Release
5. **Result**: 
   - 11 contract deferrals created (11 × 12 = 132 entries for a year)
   - 22 G/L entries generated (2 with value, 20 with 0.00)

### Task 4 - Partial Period Inconsistency
1. Create vendor subscription contract with annual billing
2. Post purchase invoice 1 with period 01.05.2025 - 15.06.2025
3. Post purchase invoice 2 with period 16.06.2025 - 31.07.2025
4. Review generated deferrals
5. **Result**: 
   - Invoice 1: Amount divided equally between May and June (ignores partial June)
   - Invoice 2: Amount distributed daily across months (correct partial period handling)

### Task 5 - Credit Memo Deferrals
1. Create customer subscription contract with deferrals enabled
2. Post invoice for €1,000
3. Create credit memo for €1,200 (exceeding original invoice)
4. Post credit memo
5. Review contract deferrals
6. **Result**: Only the €1,000 invoice appears in deferrals; no €1,200 credit memo entry exists

### Task 6 - Double Deferrals
1. Create Customer Subscription Contract and Subscription
2. Assign subscription to contract
3. Create contract invoice
4. On the invoice line, assign a Deferral Code (standard BC deferrals)
5. Post the contract invoice
6. Check both:
   - Subscription Billing module → Contract Deferrals
   - Financial Management → Standard Deferrals
7. **Result**: Deferrals created in BOTH locations, causing double revenue deferral

### Additional context

_No response_

### I will provide a fix for a bug

- [x] I will provide a fix for a bug
