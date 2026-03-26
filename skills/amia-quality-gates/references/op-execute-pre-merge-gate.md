# Operation: Execute Pre-Merge Gate

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Required Checks](#required-checks)
- [Steps](#steps)
  - [Step 1: Check CI Status](#step-1-check-ci-status)
  - [Step 2: Check Mergeable Status](#step-2-check-mergeable-status)
  - [Step 3: Check for Conflicts](#step-3-check-for-conflicts)
  - [Step 4: Verify Approval Validity](#step-4-verify-approval-validity)
  - [Step 5: Check Branch Freshness](#step-5-check-branch-freshness)
  - [Step 6: Apply Gate Decision](#step-6-apply-gate-decision)
- [Gate Pass Criteria](#gate-pass-criteria)
- [Example](#example)
- [Handling Specific Failures](#handling-specific-failures)
  - [Merge Conflicts](#merge-conflicts)
- [Pre-Merge Gate Failed: Merge Conflicts](#pre-merge-gate-failed-merge-conflicts)
  - [CI Failing](#ci-failing)
- [Pre-Merge Gate Failed: CI Checks Failing](#pre-merge-gate-failed-ci-checks-failing)
  - [Approval Invalidated](#approval-invalidated)
- [Pre-Merge Gate Failed: Approval Invalidated](#pre-merge-gate-failed-approval-invalidated)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Final automated checks before merge. Ensures the PR is in a mergeable state with passing CI, no conflicts, and valid approvals.

## When to Use

- After Review Gate passes
- Before attempting to merge
- When gate is identified as pre-merge pending

## Prerequisites

- Review Gate passed
- PR has required approvals
- CI pipeline has run on latest commit

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to check |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| gate_passed | boolean | Whether PR is ready to merge |
| mergeable | boolean | GitHub's mergeable status |
| conflicts | boolean | Whether merge conflicts exist |
| ci_status | string | passing, failing, or pending |
| approval_valid | boolean | Whether approvals are still valid |

## Required Checks

| Check | Blocking | Description |
|-------|----------|-------------|
| CI Green | Yes | All required CI checks passing |
| No Conflicts | Yes | No merge conflicts with target branch |
| Approval Valid | Yes | Approvals not invalidated by new commits |
| Branch Up-to-Date | Warning | Branch should be updated with base |

## Steps

### Step 1: Check CI Status

```bash
python3 amia_get_pr_checks.py --pr <NUMBER> --required-only
```

Verify all required checks are passing:

```bash
gh pr checks <NUMBER> --required
```

### Step 2: Check Mergeable Status

```bash
gh pr view <NUMBER> --json mergeable,mergeStateStatus
```

Possible values:

- `MERGEABLE` - Can be merged
- `CONFLICTING` - Has merge conflicts
- `UNKNOWN` - Status being calculated

### Step 3: Check for Conflicts

```bash
gh pr view <NUMBER> --json mergeable --jq '.mergeable'
```

If `CONFLICTING`, gate fails.

### Step 4: Verify Approval Validity

Check if approvals are still valid (not dismissed by new commits):

```bash
gh pr view <NUMBER> --json reviewDecision,reviews
```

### Step 5: Check Branch Freshness

Check if branch is up-to-date with base:

```bash
gh pr view <NUMBER> --json mergeStateStatus --jq '.mergeStateStatus'
```

Status values:

- `CLEAN` - Ready to merge
- `BEHIND` - Branch needs update (warning)
- `BLOCKED` - Branch protection blocking
- `DIRTY` - Has conflicts
- `UNSTABLE` - CI failing

### Step 6: Apply Gate Decision

If all checks pass:

```bash
gh pr edit <NUMBER> --remove-label "gate:pre-merge-pending" --add-label "gate:pre-merge-passed"
```

If any check fails:

```bash
gh pr edit <NUMBER> --add-label "gate:pre-merge-failed"
```

## Gate Pass Criteria

ALL of these must be true:

- [ ] All required CI checks are passing
- [ ] No merge conflicts
- [ ] At least one valid approval exists
- [ ] Not blocked by branch protection

## Example

```bash
# Check all pre-merge conditions
gh pr view 123 --json mergeable,mergeStateStatus,reviewDecision,reviewRequests

# Example output:
{
  "mergeable": "MERGEABLE",
  "mergeStateStatus": "CLEAN",
  "reviewDecision": "APPROVED",
  "reviewRequests": []
}

# All checks pass - apply label
gh pr edit 123 --remove-label "gate:pre-merge-pending" --add-label "gate:pre-merge-passed"
```

## Handling Specific Failures

### Merge Conflicts

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Pre-Merge Gate Failed: Merge Conflicts

This PR has merge conflicts with the target branch.

**Action Required**: Resolve conflicts and push updated code.

```bash
git fetch origin
git checkout <branch>
git merge origin/main
# Resolve conflicts
git add .
git commit -m "Resolve merge conflicts"
git push
```

EOF
)"

```

### CI Failing

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Pre-Merge Gate Failed: CI Checks Failing

The following required checks are failing:
<LIST_OF_FAILING_CHECKS>

**Action Required**: Fix failing tests/builds and push updated code.
EOF
)"
```

### Approval Invalidated

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Pre-Merge Gate Failed: Approval Invalidated

New commits have been pushed since approval. A re-review is required.

**Action Required**: Request re-review from approvers.
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| Mergeable status UNKNOWN | Wait and retry (GitHub calculating) |
| Branch protection blocking | Check protection rules, may need admin |
| CI stuck pending | Wait with timeout, escalate if stuck |

## Related Operations

- [op-execute-review-gate.md](op-execute-review-gate.md) - Previous gate
- [op-execute-post-merge-gate.md](op-execute-post-merge-gate.md) - Next after merge
- [op-escalate-failure.md](op-escalate-failure.md) - If gate fails
