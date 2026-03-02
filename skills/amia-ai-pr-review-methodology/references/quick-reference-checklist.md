# Quick Reference Checklist

## Table of Contents

- C.1 When to use this checklist
- C.2 The 12-item pre-approval checklist
- C.3 How to handle checklist failures
- C.4 Example: Walking through the checklist for a sample PR

---

## C.1 When to use this checklist

Use this checklist as the final step before submitting your review. After completing all phases (Context Gathering, Structured Analysis, Evidence Requirements, and Review Output), run through this checklist to confirm nothing was missed.

This checklist is a rapid sanity check, not a replacement for the full analysis. If you find a failure during the checklist, go back to the relevant phase or dimension to investigate further.

The checklist is also useful as a standalone tool for quick reviews of small, low-risk PRs where the full 4-phase methodology would be disproportionate.

---

## C.2 The 12-item pre-approval checklist

Before approving any PR, verify each item. Mark each as PASS, FAIL, or N/A (not applicable).

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | **Read complete files, not just the diff.** Did you read the full current version of every modified file (not just the changed lines)? | PASS / FAIL | If FAIL: You may miss existing solutions, patterns, or context. Go back to Phase 1. |
| 2 | **Understood the actual problem and its root cause.** Can you state the root cause in one sentence? | PASS / FAIL | If FAIL: The fix may be treating symptoms. Go back to Dimension 1 (Problem Verification). |
| 3 | **Verified no duplicate or existing solution.** Did you search the codebase for existing code that handles this case? | PASS / FAIL | If FAIL: The change may be redundant. Go back to Dimension 2 (Redundancy Check). |
| 4 | **Validated all paths and commands exist on target systems.** For every file path, binary path, or command referenced in the PR, is there evidence it exists? | PASS / FAIL / N/A | If FAIL: Request evidence from the author. See Dimension 3 (System Integration). N/A if the PR does not reference paths or commands. |
| 5 | **Checked cross-platform compatibility.** If the software supports multiple platforms, does the PR work on all of them? | PASS / FAIL / N/A | If FAIL: Request multi-platform test results. N/A if the software targets a single platform. |
| 6 | **Confirmed testing is adequate.** Does the PR include before/after demonstration, edge case tests, and an automated regression test? | PASS / FAIL | If FAIL: Request additional tests. See Dimension 1, section D1.6. |
| 7 | **Reviewed for security implications.** Does the PR introduce any new attack vectors, expose sensitive data, or handle user input unsafely? | PASS / FAIL / N/A | If FAIL: Flag as a blocking issue. See Dimension 4, section D4.5. N/A if the change has no security surface. |
| 8 | **Assessed maintainability and long-term impact.** Is this a maintainable solution, or a quick fix that creates technical debt? | PASS / FAIL | If FAIL: Suggest a more sustainable approach. See Dimension 4, section D4.3. |
| 9 | **Challenged assumptions with evidence.** For every assumption the PR makes, is there evidence (not just reasoning) that the assumption is correct? | PASS / FAIL | If FAIL: List the unverified assumptions and request evidence. See Dimension 5, section D5.2. |
| 10 | **Applied the reversibility test.** If the change were removed, would the problem return? Can the author demonstrate this? | PASS / FAIL | If FAIL: The fix may be a false positive. See Dimension 5, section D5.7. |
| 11 | **Requested any missing evidence.** Did you compile a list of all required evidence and include it in your review? | PASS / FAIL | If FAIL: Add the missing evidence items to the Required Evidence section of your review output. |
| 12 | **Provided constructive, specific, actionable feedback.** Is your review specific (references files and line numbers), actionable (tells the author what to do), and constructive (respectful and helpful)? | PASS / FAIL | If FAIL: Revise your review. See review-output-template.md, section T.6. |

---

## C.3 How to handle checklist failures

If any checklist item fails:

1. **Do not approve the PR.** A failed checklist item indicates an unresolved concern.

2. **Go back to the relevant phase or dimension.** The "Notes" column in the checklist table tells you where to look.

3. **Add the finding to your review output.** Include it in the appropriate section:
   - Failures in items 1-3: Add to "Red Flags" or "Critical Questions"
   - Failures in items 4-5: Add to "Required Evidence"
   - Failures in item 6: Add to "Testing Feedback"
   - Failures in item 7: Add to "Red Flags" (blocking)
   - Failures in items 8-9: Add to "Questions and Concerns"
   - Failure in item 10: Add to "Red Flags" (this is a strong false positive indicator)
   - Failure in item 11: Add the items to "Required Evidence"
   - Failure in item 12: Revise your review before submitting

4. **Set your recommendation to REQUEST CHANGES** if any of items 1, 2, 7, or 10 fail. These are the most critical checks.

---

## C.4 Example: Walking through the checklist for a sample PR

**PR:** "Add retry logic for database connections to handle transient ConnectionResetError"

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Read complete files | PASS | Read `db_client.py` (180 lines) and `config.py` (45 lines) in full |
| 2 | Understood root cause | PASS | Root cause: intermittent TCP resets from the database load balancer during idle connections. Documented in the linked issue with production logs. |
| 3 | No duplicate solution | PASS | Searched for "retry", "reconnect", "backoff" in the codebase. No existing retry logic for database connections. |
| 4 | Paths/commands verified | N/A | No file paths or commands in this PR. |
| 5 | Cross-platform compatibility | N/A | Server-side code, runs only on Linux production servers. |
| 6 | Testing adequate | FAIL | The PR includes a unit test that mocks the ConnectionResetError, but no integration test that demonstrates the retry working with an actual database connection. The mock test verifies the retry count but not the actual recovery. |
| 7 | Security reviewed | PASS | No new user input handling, no credential changes. The retry loop has a maximum retry count (3) so it cannot be used for denial of service. |
| 8 | Maintainability assessed | PASS | The retry logic uses a well-structured decorator pattern that can be reused for other connection types. Code is well-commented. |
| 9 | Assumptions challenged | FAIL | The PR assumes the ConnectionResetError is always transient. If the error is caused by a persistent issue (wrong credentials, firewall rule change), the retry will fail 3 times and then raise the same error, delaying the failure by the backoff time. |
| 10 | Reversibility test | PASS | The author demonstrated: without the fix, the application crashes on ConnectionResetError. With the fix, it retries and succeeds. Reverting the fix restores the crash. |
| 11 | Missing evidence requested | FAIL | Need to add: integration test results, and clarification on assumption about error transience. |
| 12 | Constructive feedback | PASS | Review is specific, references line numbers, and provides actionable suggestions. |

**Result:** Items 6, 9, and 11 failed. The recommendation is REQUEST CHANGES with two required actions:

1. Add an integration test (or at minimum, provide evidence that the retry succeeds with an actual database restart scenario).
2. Address the assumption that ConnectionResetError is always transient. Consider adding a check for persistent errors (for example, if all 3 retries fail, log a warning suggesting the issue may not be transient).
