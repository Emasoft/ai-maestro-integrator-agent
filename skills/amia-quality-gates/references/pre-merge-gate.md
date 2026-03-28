# Pre-Merge Gate

> **MULTI-REPO RULE:** All `gh` commands MUST include `--repo "$OWNER/$REPO"` since the integrator works across multiple repos.

## Table of Contents

- [Purpose](#purpose)
- [Required Checks](#required-checks)
  - [1. CI Pipeline Success](#1-ci-pipeline-success)
  - [2. No Merge Conflicts](#2-no-merge-conflicts)
  - [3. Valid Approval](#3-valid-approval)
  - [4. Branch Up-to-Date](#4-branch-up-to-date)
- [Warning Conditions (Non-Blocking)](#warning-conditions-non-blocking)
- [Gate Pass Procedure](#gate-pass-procedure)
- [Gate Fail Procedure](#gate-fail-procedure)
- [Merge Strategies](#merge-strategies)
  - [Squash Merge (Default)](#squash-merge-default)
  - [Merge Commit](#merge-commit)
  - [Rebase Merge](#rebase-merge)
- [Re-Evaluation Triggers](#re-evaluation-triggers)
- [Troubleshooting](#troubleshooting)
  - [CI Stuck in Pending](#ci-stuck-in-pending)
  - [Approval Disappeared](#approval-disappeared)
  - [Intermittent Merge Conflicts](#intermittent-merge-conflicts)
  - [Fast-Moving Main Branch](#fast-moving-main-branch)

## Purpose

The Pre-Merge Gate performs final checks immediately before merging to ensure the PR is safe to integrate into the main branch.

## Required Checks

### 1. CI Pipeline Success

**Check**: All CI jobs pass on the PR branch
**Command**: `gh pr checks $PR_NUMBER`
**Pass Criteria**: All required checks show green status
**Failure Action**: Block merge, comment with failing job details

**Re-run CI if needed**:

```bash
gh pr checks $PR_NUMBER --watch
# If failed, re-run
gh workflow run ci.yml --ref $PR_BRANCH
```

### 2. No Merge Conflicts

**Check**: PR branch can be merged cleanly into main
**Command**: `gh pr view $PR_NUMBER --json mergeable -q .mergeable`
**Pass Criteria**: Returns `MERGEABLE`
**Failure Action**: Request rebase from author

**Resolution**:

```bash
gh pr comment $PR_NUMBER --body "❌ Pre-merge gate blocked: Merge conflicts detected

Please rebase your branch:
\`\`\`bash
git fetch origin
git rebase origin/main
# Resolve conflicts
git push --force-with-lease
\`\`\`"
```

### 3. Valid Approval

**Check**: PR has required approval(s) and approval is still valid
**Command**: `gh pr view $PR_NUMBER --json reviewDecision -q .reviewDecision`
**Pass Criteria**: Returns `APPROVED`
**Failure Action**: Request re-review if stale

**Approval Validity Rules**:

- Approval is **stale** if significant changes pushed after approval
- "Significant" = more than 10 lines changed or architectural changes
- Stale approvals require re-review

### 4. Branch Up-to-Date

**Check**: PR branch includes latest main changes
**Command**: Compare PR base commit with current main HEAD
**Pass Criteria**: PR base is current main HEAD or very recent (< 5 commits behind)
**Failure Action**: Request rebase (warning only if < 5 commits behind)

## Warning Conditions (Non-Blocking)

| Condition | Warning Label | Trigger |
|-----------|--------------|---------|
| Slow CI | `gate:slow-ci` | CI duration > 15 minutes |
| Flaky test observed | `gate:flaky-test` | Test passed after retry |
| New warnings | `gate:new-warnings` | Build warnings introduced |
| Performance regression | `gate:perf-regression` | Benchmark shows slowdown |

## Gate Pass Procedure

```bash
# Verify all pre-merge checks
gh pr checks $PR_NUMBER
gh pr view $PR_NUMBER --json mergeable,reviewDecision

# All green, apply label
gh pr edit $PR_NUMBER --add-label "gate:pre-merge-passed"
gh pr edit $PR_NUMBER --remove-label "gate:pre-merge-pending"

# Proceed to merge
gh pr comment $PR_NUMBER --body "✅ Pre-merge gate passed. All systems green. Proceeding with merge."

# Execute merge
gh pr merge $PR_NUMBER --squash --delete-branch
```

## Gate Fail Procedure

```bash
# Apply failed label
gh pr edit $PR_NUMBER --add-label "gate:pre-merge-failed"

# Comment with specific failure
gh pr comment $PR_NUMBER --body "❌ Pre-merge gate failed:

**CI Status**: [PASS/FAIL with details]
**Merge Conflicts**: [YES/NO]
**Approval Valid**: [YES/NO]
**Branch Up-to-Date**: [YES/NO]

Please address the issues above. Gate will re-evaluate when:
- CI is re-run and passes
- Conflicts are resolved and pushed
- Approval is refreshed (if needed)
- Branch is rebased (if needed)"

# Follow Escalation Path C if unresolved
```

## Merge Strategies

### Squash Merge (Default)

**Use when**: Most PRs (consolidates commits)
**Command**: `gh pr merge $PR_NUMBER --squash --delete-branch`

### Merge Commit

**Use when**: Preserving commit history is important
**Command**: `gh pr merge $PR_NUMBER --merge --delete-branch`

### Rebase Merge

**Use when**: Linear history desired, small PRs
**Command**: `gh pr merge $PR_NUMBER --rebase --delete-branch`

**Team Policy**: Document preferred merge strategy in repository CONTRIBUTING.md

## Re-Evaluation Triggers

Pre-Merge Gate re-evaluates when:

- CI jobs complete
- New commits pushed
- Conflicts resolved
- Approval state changes
- Manual trigger via `/amia-run-gate pre-merge` command

## Troubleshooting

### CI Stuck in Pending

**Symptom**: CI shows "pending" indefinitely

**Resolution**:

1. Check GitHub Actions for queued/stalled jobs
2. Cancel and re-run if stuck
3. Check for infrastructure issues
4. If persistent, escalate to AMOA

### Approval Disappeared

**Symptom**: PR was approved but now shows no approval

**Resolution**:

1. Check if new commits invalidated approval (GitHub policy)
2. Check if reviewer was removed from repository
3. Request fresh approval from reviewer
4. Document in PR if approval policy changed

### Intermittent Merge Conflicts

**Symptom**: Conflicts appear/disappear

**Resolution**:

1. Author should pull latest main and rebase
2. Push clean resolved branch
3. Wait for conflict status to stabilize
4. If GitHub UI is glitchy, use git CLI to verify

### Fast-Moving Main Branch

**Symptom**: Main branch advances rapidly, PR constantly outdated

**Resolution**:

1. If < 5 commits behind: Accept minor staleness
2. If > 5 commits behind: Request rebase
3. Consider using merge queue if project supports it
4. Prioritize PR merging to reduce staleness window
