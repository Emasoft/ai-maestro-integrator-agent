# Review Output Template

## Table of Contents

- T.1 When to generate the review output
- T.2 The complete review output template (copy-paste ready)
- T.3 How to fill each section of the template
- T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
- T.5 Setting the confidence level: High, Medium, or Low
- T.6 Writing the author note
- T.7 Example: A completed review output

---

## T.1 When to generate the review output

Generate the review output after completing all preceding phases:

1. Phase 1 (Context Gathering) -- completed
2. Phase 2 (Structured Analysis with all 5 dimensions) -- completed
3. Phase 3 (Evidence Requirements) -- compiled
4. Scenario-specific protocols -- applied if relevant

The review output is the deliverable of the entire review process. It synthesizes all findings into a single, structured document that the PR author and other reviewers can act on.

---

## T.2 The complete review output template (copy-paste ready)

Copy the template below and fill in each section. Remove the instructional comments (lines starting with `INSTRUCTION:`) before submitting.

```markdown
## PR Review: [PR Title]

### Summary

[INSTRUCTION: Write one paragraph summarizing what the PR does and your overall assessment.
Include: the purpose of the PR, the approach taken, and whether the approach is sound.]

---

### Strengths

[INSTRUCTION: List specific things done well. Be concrete, not generic.
Bad: "Good code quality." Good: "The error handling in process_csv() covers all edge cases including empty files, malformed headers, and encoding errors."]

- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

---

### Questions and Concerns

#### Critical Questions (Must be answered before merge):

[INSTRUCTION: These are blocking questions. The PR cannot be approved until the author
provides satisfactory answers with evidence.]

1. [Question requiring evidence or clarification]
2. [Question requiring evidence or clarification]

#### Non-Critical Questions (For discussion):

[INSTRUCTION: These are non-blocking questions. They may improve the PR but are not
required for approval.]

1. [Question for improvement or understanding]
2. [Question for improvement or understanding]

---

### Red Flags (Blocking Issues)

[INSTRUCTION: List critical issues that MUST be resolved before merge.
These are findings from the 5-dimension analysis that indicate the PR may be incorrect,
redundant, insecure, or a false positive.
If none: Write "None identified."]

- [Blocking issue 1 with explanation]
- [Blocking issue 2 with explanation]

---

### Required Evidence

[INSTRUCTION: List specific evidence the author must provide.
Each item should specify exactly what to provide and how (e.g., terminal output, test results,
documentation links).]

Please provide the following before this PR can be approved:

- [ ] [Specific evidence needed -- e.g., "Output of `ls -la /path/from/pr` on Ubuntu 22.04"]
- [ ] [Specific evidence needed -- e.g., "Before/after benchmark with 5+ runs"]
- [ ] [Specific evidence needed -- e.g., "Regression test for the empty input case"]

---

### Suggestions (Non-blocking)

[INSTRUCTION: List alternative approaches, optimizations, or improvements the author
could consider. These are optional and will not block approval.]

- [Suggestion 1]
- [Suggestion 2]

---

### Testing Feedback

**Current test coverage:** [INSTRUCTION: Assess whether the test coverage is adequate.
Example: "Tests cover the main success path but not the error cases."]

**Recommendations:**

- [Specific test case to add -- e.g., "Add test for empty input file"]
- [Edge case to cover -- e.g., "Test with Unicode characters in file paths"]

---

### Documentation

- [ ] Code is well-commented (non-obvious logic is explained)
- [ ] PR description clearly explains the change and its purpose
- [ ] Breaking changes are documented (if applicable)
- [ ] Updated relevant documentation files (README, API docs) if needed

---

### Final Recommendation

**Status:** [APPROVE | REQUEST CHANGES | COMMENT]

**Reasoning:** [INSTRUCTION: Clear explanation of your decision. Reference specific
findings from the analysis.]

**Confidence Level:** [High | Medium | Low]

[INSTRUCTION: See section T.5 for guidance on setting the confidence level.]

---

### For the Author

[INSTRUCTION: See section T.6 for guidance on writing this note.
This is a personal, constructive note to the author. Acknowledge their effort,
explain your reasoning, and clarify next steps.]
```

---

## T.3 How to fill each section of the template

### Summary

Write one paragraph that answers three questions:
1. What does the PR do?
2. What approach does it take?
3. Is the approach sound?

**Example:** "This PR adds retry logic to the database connection handler to address intermittent ConnectionResetError failures reported in production. The approach wraps the connection attempt in a retry loop with exponential backoff, retrying up to 3 times before raising the error. The approach is sound for transient errors but needs verification that the underlying cause is indeed transient and not a persistent configuration issue."

### Strengths

Be specific. Reference file names, function names, and line numbers. Generic praise ("nice work") is not useful.

**Example:** "The retry logic in `db_client.py:connect()` correctly uses exponential backoff with jitter, which prevents thundering herd effects when multiple clients reconnect simultaneously."

### Questions and Concerns

Separate critical (blocking) from non-critical (discussion). Critical questions must be answered before the PR can be approved. Non-critical questions are for the author's consideration.

### Red Flags

Only list findings that are blocking. A red flag means "this issue must be resolved or explained before the PR is safe to merge." Red flags typically come from the dimension analysis (sections D1.7, D2.6, D3.6, D4.7, D5.8).

### Required Evidence

Each evidence item must be actionable. Tell the author exactly what to do and what output to provide.

### Suggestions

Non-blocking improvements. The PR can be approved without these, but they would make it better.

### Testing Feedback

Assess the current test coverage and identify gaps. Be specific about what tests to add.

### Documentation

Use the checklist. Check each item based on the PR's actual state.

---

## T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT

| Recommendation | When to Use |
|---------------|-------------|
| **APPROVE** | All 5 dimensions pass, all evidence is provided, no red flags, tests are adequate |
| **REQUEST CHANGES** | One or more red flags exist, critical evidence is missing, or the approach has fundamental issues |
| **COMMENT** | The review is informational (no decision needed), or you are providing feedback on a draft PR |

**APPROVE does not mean the PR is perfect.** It means the PR is correct, safe, and ready to merge. Suggestions can be addressed in follow-up PRs.

**REQUEST CHANGES should always include specific actions.** Do not just say "needs work." List exactly what the author needs to do:
- "Provide benchmark results with 5+ runs"
- "Add a regression test for the empty file case"
- "Remove the redundant path at line 42"

---

## T.5 Setting the confidence level: High, Medium, or Low

| Level | Meaning | When to Use |
|-------|---------|-------------|
| **High** | You are confident in your assessment and have verified all key claims | You read the complete files, verified paths/commands, and all 5 dimensions are thoroughly evaluated |
| **Medium** | You are reasonably confident but some aspects could not be fully verified | You could not verify some paths on target systems, or you are unfamiliar with part of the codebase |
| **Low** | Your assessment is based on limited information or partial analysis | The PR touches code you have not worked with before, or critical evidence is unavailable |

Always state your confidence level honestly. A low-confidence review is more useful than an overconfident one, because it tells the author which areas need additional review from someone with more domain knowledge.

---

## T.6 Writing the author note

The author note is a personal, constructive message to the PR author. Its purpose is to:

1. **Acknowledge effort.** The author spent time on this PR. Recognize that.
2. **Explain reasoning.** If you are requesting changes, explain why clearly.
3. **Clarify next steps.** Tell the author exactly what to do next.
4. **Be constructive, not adversarial.** Frame feedback as "help me understand" rather than "you did this wrong."

**Example author note (REQUEST CHANGES):**

"Thank you for investigating the connection timeout issue. The retry logic approach is solid. I have a few concerns about cache invalidation and benchmark methodology that I would like to see addressed before we merge. The specific items are listed in the Required Evidence section above. Once those are provided, I expect this will be ready to approve. Let me know if any of the requested evidence is difficult to obtain, and we can discuss alternatives."

**Example author note (APPROVE):**

"Clean implementation with good test coverage. The exponential backoff with jitter is a nice touch. I left a couple of non-blocking suggestions about documentation, but this is ready to merge as-is. Good work."

---

## T.7 Example: A completed review output

```markdown
## PR Review: Fix CSV parser crash on empty files

### Summary

This PR fixes a crash in the CSV parser when processing files with no data rows.
The parser assumed at least one row existed and accessed `rows[0]` without checking
for an empty list. The fix adds an empty-file check that returns an empty result
with a warning log message. The approach is sound and addresses the root cause.

---

### Strengths

- Root cause clearly identified: missing bounds check on the rows list
  in `processor.py:process_csv()` at line 87
- Before/after demonstration provided in the PR description
- Regression test added (`test_process_csv_with_empty_file`)
- Warning message is informative ("empty.csv has no data rows. Skipping.")

---

### Questions and Concerns

#### Critical Questions (Must be answered before merge):

1. What happens with a CSV file that has a header row but no data rows?
   The current fix checks `len(rows) == 0`, but a file with only a header
   would have `len(rows) == 1` and proceed to process zero data rows.
   Is this handled correctly?

#### Non-Critical Questions (For discussion):

1. Should the function return `None` or `[]` for empty files?
   Currently it returns `[]`, which is consistent with "zero results."
   Consider whether callers distinguish between "no results" and "invalid input."

---

### Red Flags (Blocking Issues)

None identified.

---

### Required Evidence

Please provide the following before this PR can be approved:

- [ ] Test result for a CSV file with a header row but no data rows
- [ ] Confirmation that all existing tests pass with the change

---

### Suggestions (Non-blocking)

- Consider also handling the case where the file contains only whitespace
  (e.g., a file with blank lines but no CSV content)
- The warning log message could include the file path for easier debugging

---

### Testing Feedback

**Current test coverage:** Tests cover the empty file case. Missing coverage for
header-only files and whitespace-only files.

**Recommendations:**

- Add test for CSV file with header but no data rows
- Add test for CSV file containing only whitespace or blank lines

---

### Documentation

- [x] Code is well-commented (the empty check has a clear comment)
- [x] PR description clearly explains the change and its purpose
- [ ] Breaking changes are documented -- N/A (no breaking changes)
- [ ] Updated relevant documentation files -- N/A

---

### Final Recommendation

**Status:** REQUEST CHANGES

**Reasoning:** The fix is correct for the empty file case, but the header-only
case needs verification. Once the author confirms behavior for header-only files
(and adds a test if needed), this is ready to approve.

**Confidence Level:** High

---

### For the Author

Good catch on the empty file crash. The fix is clean and well-tested for the
primary case. I just want to verify the header-only scenario before we merge.
The test for that case should be straightforward to add. Let me know if you
have questions about the edge cases I mentioned.
```
