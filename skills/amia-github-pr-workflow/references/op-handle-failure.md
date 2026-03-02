# Operation: Handle PR Workflow Failures


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Failure Types in Detail](#failure-types-in-detail)
  - [Verification Failures](#verification-failures)
  - [Subagent Failures](#subagent-failures)
  - [CI Failures](#ci-failures)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)
- [PR #123 Verification Failed](#pr-123-verification-failed)
  - [Failing Criteria](#failing-criteria)
  - [Recovery Approach](#recovery-approach)
  - [Next Steps](#next-steps)
- [Critical Rule](#critical-rule)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-handle-failure
---

## Purpose

Handle failures in PR workflow by identifying the issue, determining recovery approach, and delegating fixes.

## When to Use

- Verification fails (criteria not met)
- Subagent reports failure
- CI checks fail
- Merge conflicts detected
- Unexpected errors occur

## Prerequisites

- Failure identified with details
- Root cause understood
- Fix is within scope (not blocked)

## Steps

1. **Identify failure type**:

   | Failure Type | Indicators | Severity |
   |--------------|------------|----------|
   | Verification failure | `complete: false` in verification | Medium |
   | Subagent failure | `[FAILED]` in report | Medium |
   | CI failure | Checks failing | Medium |
   | Merge conflict | `mergeable: CONFLICTING` | High |
   | Auth/permission error | 401/403 responses | High |
   | Unexpected error | Exception, crash | High |

2. **Determine recovery approach**:

   | Failure | Recovery | Action |
   |---------|----------|--------|
   | Failing test | Fixable | Delegate to implementation subagent |
   | Unresolved thread | Fixable | Delegate response/resolution |
   | Merge conflict | Fixable | Delegate rebase/conflict resolution |
   | Permission denied | Blocked | Escalate to user |
   | Repeated failure | Blocked | Escalate with details |

3. **If fixable**: Delegate repair work
   ```
   ## Fix Task for PR #<number>

   ### Issue
   <specific failure description>

   ### Required Fix
   <specific actions to take>

   ### Success Criteria
   - <criterion that was failing> now passes
   - Verification script returns complete: true
   ```

4. **If blocked**: Escalate to user
   ```
   ## PR #<number> Blocked - User Decision Required

   ### Issue
   <failure description>

   ### Attempted Recovery
   <what was tried>

   ### Options
   1. <option_1>
   2. <option_2>

   Please advise.
   ```

5. **Log the failure** and recovery attempt

6. **Re-verify** after fix attempt

## Failure Types in Detail

### Verification Failures

| Failing Criterion | Fix Approach |
|-------------------|--------------|
| reviews_addressed | Delegate: respond to each review comment |
| comments_acknowledged | Delegate: respond to PR comments |
| no_new_comments | Wait 45s and re-verify |
| ci_passing | Delegate: fix failing tests/builds |
| no_unresolved_threads | Delegate: resolve each thread |
| merge_eligible | Delegate: rebase to resolve conflicts |
| commits_pushed | Delegate: push pending commits |

### Subagent Failures

| Failure | Recovery |
|---------|----------|
| Task too complex | Break into smaller tasks, re-delegate |
| Missing context | Re-delegate with more context |
| Timeout | Re-delegate with longer timeout or simpler scope |
| Crash | Check logs, re-delegate |

### CI Failures

| Failure | Recovery |
|---------|----------|
| Test failure | Delegate test fix |
| Build failure | Delegate build fix |
| Lint failure | Delegate lint fix |
| Flaky test | Retry CI, if persists then fix |

## Output

| Field | Type | Description |
|-------|------|-------------|
| failure_type | string | Category of failure |
| recovery_approach | string | fix, escalate, or retry |
| delegated_to | string | Subagent handling fix (if applicable) |
| escalation_reason | string | Why user input needed (if blocked) |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Fix attempt fails | Root cause not addressed | Re-analyze, try different approach |
| Repeated failures | Underlying issue | Escalate after 3 attempts |
| Cascade failures | One fix breaks another | Rollback, re-analyze dependencies |

## Example

```
## PR #123 Verification Failed

### Failing Criteria
- ci_passing: false
  - `test_user_login` failing with "AssertionError: expected 200, got 401"

### Recovery Approach
Delegating fix to implementation subagent with task:

"Fix test_user_login in tests/test_auth.py. The test expects 200 but gets 401.
Check authentication setup in test fixtures. Success criteria: all tests pass."

### Next Steps
1. Subagent fixes test
2. Re-run verification
3. Report to user when complete
```

## Critical Rule

**Maximum 3 fix attempts** before escalating. If the same failure persists after 3 delegated fixes, escalate to user with full context.
