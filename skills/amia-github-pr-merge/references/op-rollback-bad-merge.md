---
name: op-rollback-bad-merge
description: Rollback a merge that introduced issues to the target branch
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Rollback Bad Merge


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Rollback Options](#rollback-options)
- [Procedure: Option 1 - Revert Commit (Recommended)](#procedure-option-1-revert-commit-recommended)
- [Procedure: Option 2 - Hotfix PR](#procedure-option-2-hotfix-pr)
- [Procedure: Option 3 - Force Reset (DESTRUCTIVE)](#procedure-option-3-force-reset-destructive)
- [Example: Standard Revert Workflow](#example-standard-revert-workflow)
- [Safety Checklist](#safety-checklist)
- [Post-Rollback Actions](#post-rollback-actions)
- [Error Handling](#error-handling)
- [Critical Warnings](#critical-warnings)
- [Related Operations](#related-operations)

## Purpose

Revert or undo a merge that introduced bugs, broken code, or other issues to the target branch. This operation should be used when a merged PR causes problems that need immediate resolution.

## When to Use

- After merge introduces bugs or regressions
- When CI/CD pipeline fails after merge
- When production issues are traced to a merge
- When code review reveals critical issues post-merge

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository write access
- Git installed locally
- Knowledge of the problematic merge commit SHA

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| PR number | Integer | Yes | The merged PR to rollback |
| Repository | String | Yes | Repository in owner/repo format |
| Merge commit SHA | String | Yes | SHA of the merge commit to revert |

## Rollback Options

| Method | Impact | Use When |
|--------|--------|----------|
| Revert commit | Safe, preserves history | Preferred - creates new commit undoing changes |
| Reset + force push | DESTRUCTIVE | Only with explicit approval, rewrites history |
| Hotfix PR | Safe, allows fixes | When partial rollback or fix is possible |

## Procedure: Option 1 - Revert Commit (Recommended)

1. Identify the merge commit SHA
2. Create a revert commit
3. Push the revert
4. Create a new PR if branch protection requires it

```bash
# Get the merge commit SHA
gh pr view <PR_NUMBER> --repo <OWNER/REPO> --json mergeCommit

# Create revert commit locally
git checkout main
git pull origin main
git revert -m 1 <MERGE_COMMIT_SHA>

# Push the revert
git push origin main
```

## Procedure: Option 2 - Hotfix PR

1. Create a new branch from main
2. Make the fix or revert changes
3. Create PR for the fix
4. Merge the hotfix PR

```bash
# Create hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/revert-pr-<PR_NUMBER>

# Revert the changes
git revert -m 1 <MERGE_COMMIT_SHA>

# Push and create PR
git push -u origin hotfix/revert-pr-<PR_NUMBER>
gh pr create --title "Revert PR #<PR_NUMBER>" --body "Reverting due to: [REASON]"
```

## Procedure: Option 3 - Force Reset (DESTRUCTIVE)

**WARNING**: This requires explicit user approval. It rewrites history and affects all collaborators.

```bash
# Only with explicit approval
git checkout main
git reset --hard <COMMIT_BEFORE_MERGE>
git push --force origin main  # REQUIRES EXPLICIT APPROVAL
```

## Example: Standard Revert Workflow

```bash
# Step 1: Identify the bad merge
gh pr view 123 --repo myorg/myrepo --json mergeCommit
# Output: {"mergeCommit": {"oid": "abc123def456"}}

# Step 2: Pull latest main
git checkout main
git pull origin main

# Step 3: Revert the merge commit
git revert -m 1 abc123def456
# Editor opens for commit message - describe why reverting

# Step 4: Push the revert
git push origin main

# Step 5: Verify the revert
git log --oneline -5
# Should show: "Revert 'PR title here'"
```

## Safety Checklist

Before any rollback:

- [ ] Confirmed the merge commit SHA is correct
- [ ] Identified all changes that will be reverted
- [ ] Notified team members of the rollback
- [ ] Have a plan to re-introduce fixes if needed
- [ ] Documented the reason for rollback

## Post-Rollback Actions

1. **Notify the PR author** about the rollback and reason
2. **Create an issue** tracking the problem that caused rollback
3. **Plan the fix** - either fix the original code or take different approach
4. **Document lessons learned** for future reference

## Error Handling

| Scenario | Action |
|----------|--------|
| Revert has conflicts | Resolve conflicts manually, then commit |
| Branch protection blocks push | Create revert as PR instead |
| Wrong commit reverted | Revert the revert, start over |
| Force push blocked | Request admin to temporarily disable protection |

## Critical Warnings

1. **NEVER force push without explicit approval**
2. **ALWAYS prefer revert over reset** - preserves history
3. **DOCUMENT the rollback** - why it happened, what was affected
4. **COMMUNICATE with team** - rollbacks affect everyone

## Related Operations

- [op-execute-pr-merge.md](op-execute-pr-merge.md) - The original merge
- [op-verify-merge-completion.md](op-verify-merge-completion.md) - Verify state after rollback
- [op-check-merge-readiness.md](op-check-merge-readiness.md) - For re-merge after fix
