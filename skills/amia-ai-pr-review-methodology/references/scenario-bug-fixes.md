# Scenario Protocol: Bug Fix PRs

## Table of Contents

- S-BUG.1 When to use this scenario protocol
- S-BUG.2 Original error identification
- S-BUG.3 Root cause identification requirements
- S-BUG.4 Reproduction before the fix
- S-BUG.5 Fix demonstration
- S-BUG.6 Regression test requirement
- S-BUG.7 Example: Reviewing a bug fix PR end-to-end

---

## S-BUG.1 When to use this scenario protocol

Use this protocol when the PR claims to fix a bug. A bug fix PR is identified by:

- The PR title or description mentions "fix", "bug", "error", "crash", "broken", or similar terms
- The PR is linked to a bug report or issue
- The PR modifies error handling, exception handling, or recovery logic
- The PR changes behavior to match an expected specification

This protocol requires five pieces of evidence before the PR can be approved. If any piece is missing, the PR should be marked as REQUEST CHANGES.

---

## S-BUG.2 Original error identification

**Requirement:** The original error must be clearly identified and documented.

**What to look for:**

1. The exact error message, exception type, or stack trace
2. The conditions under which the error occurs (input data, environment, user action)
3. The frequency of the error (always, intermittent, under specific conditions)

**Acceptable evidence:**

- A linked issue with the error details
- Error output pasted in the PR description
- Log files showing the error
- Screenshot of the error in the application

**Unacceptable evidence:**

- "Users reported a bug" without specifics
- "It was broken" without explaining what "broken" means
- A general description without the exact error message

**What to ask the author if the error is not identified:**

"Can you provide the exact error message or stack trace that users encountered? Without seeing the specific error, I cannot verify that your fix addresses it."

---

## S-BUG.3 Root cause identification requirements

**Requirement:** The root cause of the bug must be identified and explained in the PR description.

The root cause is different from the symptom. The symptom is what the user sees (a crash, an error message, incorrect output). The root cause is the code defect that produces the symptom.

**How to verify root cause is identified:**

1. Read the PR description's explanation of why the bug occurs.
2. Check whether the explanation describes a specific code path, a missing check, a wrong assumption, or a logic error.
3. Verify that the PR's code changes target the identified root cause (not just catching or suppressing the error).

**Example of insufficient root cause identification:**

"The application crashed because it threw a NullPointerException. Fixed by adding a null check."

This identifies the symptom (NullPointerException) but not the root cause (why is the value null?). The null check may prevent the crash but does not fix the underlying issue that produces the null value.

**Example of sufficient root cause identification:**

"The `user.profile` field is null when the user has not completed onboarding. The dashboard page accesses `user.profile.name` without checking for null. The root cause is that the dashboard page does not account for users who are still in the onboarding flow. Fixed by adding a redirect to the onboarding page when `user.profile` is null."

---

## S-BUG.4 Reproduction before the fix

**Requirement:** The author must demonstrate that the bug can be reproduced before the fix is applied.

**Why reproduction matters:**

If the bug cannot be reproduced:
- The fix cannot be verified (you cannot confirm it resolves something you cannot trigger)
- The bug may be caused by a transient condition that has already resolved
- The fix may be a false positive (see [dimension-5-false-positive-detection.md](./dimension-5-false-positive-detection.md))

**What to ask the author:**

"Can you provide reproduction steps that consistently trigger the bug on the base branch (before your changes)? Please include:
1. Starting state (clean install, specific configuration, specific data)
2. Exact steps to trigger the error
3. Expected result vs actual result
4. The platform and version where you reproduced it"

**If the bug is intermittent:**

Intermittent bugs require additional evidence. The author should:
1. Run the reproduction steps multiple times (at least 10 attempts)
2. Document the frequency (for example, "fails 3 out of 10 times")
3. After applying the fix, run the same steps the same number of times
4. Document that the failure no longer occurs

---

## S-BUG.5 Fix demonstration

**Requirement:** The author must demonstrate that the fix resolves the bug.

**What constitutes a valid demonstration:**

1. The reproduction steps from section S-BUG.4 are executed with the fix applied.
2. The error no longer occurs.
3. The correct behavior is observed.
4. The demonstration is on the same platform where the bug was reproduced.

**Before/after comparison format:**

```
BEFORE (base branch, no fix):
$ mytool process input.json
Error: NullPointerException at Dashboard.java:42
Exit code: 1

AFTER (PR branch, with fix):
$ mytool process input.json
Processing complete. Output written to output.json
Exit code: 0
```

**What to ask the author:**

"Can you show a before/after comparison? Run the reproduction steps on the base branch (error occurs), then on your branch (error does not occur)."

---

## S-BUG.6 Regression test requirement

**Requirement:** A regression test must be added that would fail without the fix and passes with the fix.

**Why regression tests are required:**

Without a regression test:
- The bug can be reintroduced by a future change
- There is no automated proof that the fix works
- Future refactoring may accidentally remove the fix without anyone noticing

**What a good regression test looks like:**

```python
def test_dashboard_handles_user_without_profile():
    """Verify that the dashboard redirects to onboarding when the user
    profile is not yet created, instead of crashing with a null reference."""
    user = create_user(onboarding_complete=False)
    response = client.get("/dashboard", user=user)
    assert response.status_code == 302
    assert response.headers["Location"] == "/onboarding"
```

This test:
- Describes the scenario in the docstring
- Sets up the specific condition that caused the bug (user without profile)
- Verifies the correct behavior (redirect, not crash)
- Would fail on the base branch (crash instead of redirect)
- Passes on the PR branch (redirect works correctly)

**What to ask the author if no regression test is provided:**

"Can you add a test that reproduces the original bug scenario? The test should fail on the base branch and pass with your fix. This prevents the bug from being reintroduced by future changes."

---

## S-BUG.7 Example: Reviewing a bug fix PR end-to-end

**PR title:** "Fix crash when processing empty CSV files"

**Step 1: Check original error identification (S-BUG.2).**

PR description says: "The application crashes with IndexError when processing a CSV file with no data rows."

Error message provided:
```
IndexError: list index out of range
  File "processor.py", line 87, in process_csv
    header = rows[0]
```

PASS -- The exact error and location are identified.

**Step 2: Check root cause identification (S-BUG.3).**

PR description says: "The `process_csv` function reads all rows from the CSV file and assumes there is at least one row (the header). When the file is empty, `rows` is an empty list and `rows[0]` raises IndexError. The root cause is the missing check for an empty file."

PASS -- The root cause (missing empty file check) is clearly identified.

**Step 3: Check reproduction (S-BUG.4).**

PR description includes reproduction steps:
```
1. Create an empty file: touch empty.csv
2. Run: python processor.py empty.csv
3. Result: IndexError at line 87
```

PASS -- Reproduction steps are provided and specific.

**Step 4: Check fix demonstration (S-BUG.5).**

PR description includes before/after:
```
BEFORE: python processor.py empty.csv -> IndexError
AFTER:  python processor.py empty.csv -> "Warning: empty.csv has no data rows. Skipping."
```

PASS -- Before/after demonstration is provided.

**Step 5: Check regression test (S-BUG.6).**

PR includes a new test:
```python
def test_process_csv_with_empty_file(tmp_path):
    """Verify that processing an empty CSV produces a warning and
    returns an empty result instead of crashing."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("")
    result = process_csv(str(empty_csv))
    assert result == []
```

PASS -- Regression test covers the bug scenario.

**Final assessment:** All five evidence requirements are met. Proceed with the standard 5-dimension analysis, paying attention to edge cases (What about a file with only a header and no data? What about a file with only whitespace?).
