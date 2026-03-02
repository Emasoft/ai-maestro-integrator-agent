# Operation: Report PR Status to User


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Output](#output)
- [Report Types](#report-types)
- [Error Handling](#error-handling)
- [Example Reports](#example-reports)
  - [Ready to Merge](#ready-to-merge)
- [PR #456 Status: Ready to Merge](#pr-456-status-ready-to-merge)
  - [Verification Results](#verification-results)
  - [Recommendation](#recommendation)
  - [Needs Work](#needs-work)
- [PR #456 Status: Needs Work](#pr-456-status-needs-work)
  - [Failing Criteria](#failing-criteria)
  - [Recommended Actions](#recommended-actions)
- [Critical Rule](#critical-rule)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-report-status
---

## Purpose

Provide clear, actionable status update to user about PR readiness and await their decision on merging.

## When to Use

- After verification passes (ready to merge)
- When user requests status update
- When significant progress made
- When blocked and need user decision

## Prerequisites

- Verification completed (op-verify-completion)
- All data gathered for report
- Clear recommendation available

## Steps

1. **Gather report data**:
   - Verification result (pass/fail)
   - Failing criteria (if any)
   - Work completed by subagents
   - Recommended next action

2. **Format status report**:

   ### For Ready PRs:
   ```
   ## PR #<number> Status: Ready to Merge

   **Title**: <pr_title>
   **Author**: <author>

   ### Verification Results
   All 8 criteria passed.

   ### Recommendation
   PR is ready for merge. Awaiting your approval.

   **Actions**:
   - Reply "merge" to merge this PR
   - Reply "hold" to keep it open
   - Reply with questions for more details
   ```

   ### For PRs Needing Work:
   ```
   ## PR #<number> Status: Needs Work

   **Title**: <pr_title>
   **Author**: <author>

   ### Failing Criteria
   - <criterion_1>: <explanation>
   - <criterion_2>: <explanation>

   ### Recommended Actions
   - <action_1>
   - <action_2>

   **Delegating fixes to subagent...**
   ```

   ### For Blocked PRs:
   ```
   ## PR #<number> Status: Blocked

   **Title**: <pr_title>
   **Author**: <author>

   ### Blocking Issues
   - <issue>: <details>

   ### User Decision Required
   <specific question or options>
   ```

3. **Send report** via appropriate channel (direct response or AI Maestro)

4. **Log report** in orchestration log

5. **Await user decision** (for ready/blocked PRs)

## Output

| Field | Type | Description |
|-------|------|-------------|
| report_type | string | ready, needs_work, blocked |
| summary | string | One-line summary |
| details | string | Full report text |
| awaiting | string | What we're waiting for |

## Report Types

| Type | User Action Required | Coordinator Action |
|------|---------------------|-------------------|
| ready | Merge decision | Wait for response |
| needs_work | None (informational) | Delegate fixes |
| blocked | Decision or guidance | Wait for response |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| User not responding | User busy or away | Wait, do not spam |
| Unclear feedback | Ambiguous response | Ask clarifying question |
| Changed requirements | User wants different approach | Adapt and re-plan |

## Example Reports

### Ready to Merge
```
## PR #456 Status: Ready to Merge

**Title**: Add user authentication module
**Author**: ai-developer

### Verification Results
All 8 criteria passed:
- Reviews addressed
- Comments acknowledged
- No new comments (45s quiet)
- CI passing (all 12 checks)
- No unresolved threads
- Merge eligible (no conflicts)
- PR still open
- All commits pushed

### Recommendation
PR is ready for merge. Awaiting your approval.

Reply "merge" to proceed, or "hold" for more review.
```

### Needs Work
```
## PR #456 Status: Needs Work

**Title**: Add user authentication module
**Author**: ai-developer

### Failing Criteria
- ci_passing: Test `test_login_invalid` failing
- no_unresolved_threads: 1 thread about error handling

### Recommended Actions
1. Fix failing test in tests/test_auth.py
2. Resolve thread about error handling approach

Delegating fixes to implementation subagent...
```

## Critical Rule

**Never merge without user approval.** Report and wait. The merge decision belongs to the user.
