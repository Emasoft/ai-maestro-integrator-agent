---
name: op-execute-post-merge-gate
description: Execute Post-Merge Gate checks (main branch health verification)
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Execute Post-Merge Gate


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Required Checks](#required-checks)
- [Steps](#steps)
  - [Step 1: Verify Merge Completed](#step-1-verify-merge-completed)
  - [Step 2: Check Main Branch CI](#step-2-check-main-branch-ci)
  - [Step 3: Wait for CI to Complete](#step-3-wait-for-ci-to-complete)
  - [Step 4: Verify No Regressions](#step-4-verify-no-regressions)
  - [Step 5: Close Related Issues](#step-5-close-related-issues)
  - [Step 6: Apply Gate Decision](#step-6-apply-gate-decision)
- [Gate Pass Criteria](#gate-pass-criteria)
- [Example](#example)
- [Failure Handling: Main Branch Broken](#failure-handling-main-branch-broken)
  - [Severity Assessment](#severity-assessment)
  - [Revert Procedure](#revert-procedure)
  - [Notification](#notification)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Verify main branch health after merge. Ensures the merge did not break the main branch and production remains stable.

## When to Use

- Immediately after PR is merged
- When monitoring main branch health
- After any merge to protected branches

## Prerequisites

- PR has been merged
- CI configured to run on main branch
- Access to main branch status

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The merged PR number |
| merge_commit | string | No | The merge commit SHA |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| gate_passed | boolean | Whether main branch is healthy |
| main_branch_status | string | passing, failing, or degraded |
| issues_closed | array | Issues closed by this merge |
| rollback_needed | boolean | Whether rollback is recommended |

## Required Checks

| Check | Critical | Description |
|-------|----------|-------------|
| Main CI Green | Yes | CI passes on main branch |
| No Regressions | Yes | No new test failures |
| Deploy Healthy | Yes | If auto-deploy, verify health |

## Steps

### Step 1: Verify Merge Completed

```bash
gh pr view <NUMBER> --json state,mergedAt,mergeCommit
```

Confirm:
- `state` is `MERGED`
- `mergedAt` has timestamp
- `mergeCommit` exists

### Step 2: Check Main Branch CI

```bash
# Get main branch status
gh api repos/{owner}/{repo}/commits/main/status
```

Or check specific workflows:
```bash
gh run list --branch main --limit 5
```

### Step 3: Wait for CI to Complete

```bash
# Poll until CI completes
python3 amia_wait_for_checks.py --branch main --timeout 600
```

### Step 4: Verify No Regressions

Compare test results before and after merge:
- No new test failures
- No decrease in coverage
- No performance degradation

### Step 5: Close Related Issues

If main branch healthy, close linked issues:
```bash
# Get linked issues
gh pr view <NUMBER> --json closingIssuesReferences

# Close each issue
gh issue close <ISSUE_NUMBER> --comment "Closed by PR #<NUMBER>"
```

See [op-close-related-issues.md](../../amia-code-review-patterns/references/op-close-related-issues.md)

### Step 6: Apply Gate Decision

If main branch healthy:
```bash
gh pr edit <NUMBER> --add-label "gate:post-merge-passed"
```

If main branch broken:
```bash
gh pr edit <NUMBER> --add-label "gate:post-merge-failed"
```

## Gate Pass Criteria

ALL of these must be true:
- [ ] Main branch CI is passing
- [ ] No new test failures introduced
- [ ] No critical errors in logs (if deployed)
- [ ] Linked issues can be closed

## Example

```bash
# Verify merge
gh pr view 123 --json state,mergeCommit
# Output: {"state":"MERGED","mergeCommit":{"oid":"abc123"}}

# Check main branch status
gh run list --branch main --limit 3
# Output:
# STATUS  WORKFLOW  BRANCH  EVENT  ID
# ✓       CI        main    push   12345
# ✓       Deploy    main    push   12346

# Apply passed label
gh pr edit 123 --add-label "gate:post-merge-passed"

# Close linked issues
gh issue close 45 --comment "Closed by PR #123"
```

## Failure Handling: Main Branch Broken

If post-merge gate fails (main branch broken):

### Severity Assessment

| Condition | Severity | Action |
|-----------|----------|--------|
| Tests failing | High | Immediate fix or revert |
| Build broken | Critical | Immediate revert |
| Deploy failed | Critical | Rollback deployment |
| Minor degradation | Medium | Track, fix in next PR |

### Revert Procedure

```bash
# Create revert PR
gh pr create --title "Revert: PR #<NUMBER>" \
    --body "Reverting due to main branch breakage" \
    --head "revert-pr-<NUMBER>"

# Or use git revert
git revert <MERGE_COMMIT>
git push origin main
```

### Notification

Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `[CRITICAL] Main Branch Broken - PR #<NUMBER>`
- **Priority**: `urgent`
- **Content**: `{"type": "post-merge-failure", "message": "PR #<NUMBER> broke main branch. CI failing. Revert recommended."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Error Handling

| Error | Action |
|-------|--------|
| CI not running on main | Trigger manually, check CI config |
| Flaky test failure | Verify it's not PR-related, re-run |
| Deploy timeout | Check deployment logs, may need manual intervention |

## Related Operations

- [op-execute-pre-merge-gate.md](op-execute-pre-merge-gate.md) - Previous gate
- [op-escalate-failure.md](op-escalate-failure.md) - Escalation Path D for failures
- [op-close-related-issues.md](../../amia-code-review-patterns/references/op-close-related-issues.md) - Issue closure
