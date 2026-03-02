---
name: op-approve-and-merge
description: Operation procedure for approving a PR and preparing for merge.
workflow-instruction: "support"
procedure: "support-skill"
---

# Operation: Approve and Merge


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify All Checks Pass](#step-1-verify-all-checks-pass)
  - [Step 2: Update Review Label to Approved](#step-2-update-review-label-to-approved)
  - [Step 3: Submit Approval Review](#step-3-submit-approval-review)
  - [Step 4: Get Linked Issue Number](#step-4-get-linked-issue-number)
  - [Step 5: Merge PR (if authorized)](#step-5-merge-pr-if-authorized)
  - [Step 6: Update Linked Issue Status](#step-6-update-linked-issue-status)
  - [Step 7: Verify Merge](#step-7-verify-merge)
- [Example](#example)
- [Merge Strategies](#merge-strategies)
- [Post-Merge Checklist](#post-merge-checklist)
- [Error Handling](#error-handling)
- [Notes](#notes)

## Purpose

After successful review, approve the PR, update labels, and either merge or prepare for merge.

## When to Use

- When review finds no issues
- When all requested changes have been addressed
- When PR is ready to merge

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- PR number being reviewed
- All checks passing
- No merge conflicts

## Procedure

### Step 1: Verify All Checks Pass

```bash
gh pr checks $PR_NUMBER
# All checks should show ✓
```

### Step 2: Update Review Label to Approved

```bash
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:approved"
# Also remove changes-requested if present
gh pr edit $PR_NUMBER --remove-label "review:changes-requested" 2>/dev/null || true
```

### Step 3: Submit Approval Review

```bash
gh pr review $PR_NUMBER --approve --body "## Approved

Review complete. All criteria met:
- [x] Code quality acceptable
- [x] Tests present and passing
- [x] Documentation updated
- [x] No security concerns

Ready to merge."
```

### Step 4: Get Linked Issue Number

```bash
# Find linked issue from PR body
LINKED_ISSUE=$(gh pr view $PR_NUMBER --json body --jq '.body' | grep -oE "(closes|fixes|resolves) #[0-9]+" | grep -oE "[0-9]+")
echo "Linked issue: #$LINKED_ISSUE"
```

### Step 5: Merge PR (if authorized)

```bash
# Squash merge (preferred)
gh pr merge $PR_NUMBER --squash --delete-branch

# Or standard merge
gh pr merge $PR_NUMBER --merge --delete-branch
```

### Step 6: Update Linked Issue Status

```bash
if [ -n "$LINKED_ISSUE" ]; then
  gh issue edit $LINKED_ISSUE --remove-label "status:ai-review" --add-label "status:done"

  # Remove assignment if issue is complete
  ASSIGN_LABEL=$(gh issue view $LINKED_ISSUE --json labels --jq '.labels[].name | select(startswith("assign:"))')
  if [ -n "$ASSIGN_LABEL" ]; then
    gh issue edit $LINKED_ISSUE --remove-label "$ASSIGN_LABEL"
  fi
fi
```

### Step 7: Verify Merge

```bash
gh pr view $PR_NUMBER --json state --jq '.state'
# Expected: MERGED
```

## Example

**Scenario:** Approve and merge PR #45 which closes issue #78.

```bash
# Step 1: Verify checks
gh pr checks 45
# All ✓

# Step 2: Update label
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:approved"

# Step 3: Submit approval
gh pr review 45 --approve --body "## Approved

Review complete. All criteria met:
- [x] Code quality acceptable
- [x] Tests present and passing
- [x] Documentation updated
- [x] No security concerns

Ready to merge."

# Step 4: Merge
gh pr merge 45 --squash --delete-branch

# Step 5: Update linked issue
gh issue edit 78 --remove-label "status:ai-review" --add-label "status:done"
gh issue edit 78 --remove-label "assign:implementer-1"

# Step 6: Verify
gh pr view 45 --json state
# Output: "MERGED"
```

## Merge Strategies

| Strategy | When to Use |
|----------|-------------|
| Squash | Default - clean history |
| Merge | Preserve all commits (complex features) |
| Rebase | Linear history preferred |

## Post-Merge Checklist

- [ ] PR state is MERGED
- [ ] Branch deleted
- [ ] Linked issue marked done
- [ ] Assignment label removed
- [ ] Author notified (if agent)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Merge conflict | Branch out of date | Ask author to rebase |
| Checks failing | CI issues | Wait for fix, don't force merge |
| Protected branch | Branch rules | Ensure all requirements met |
| No linked issue | Missing reference | Check PR description or find manually |

## Notes

- Never merge with failing checks
- Always delete branch after merge to keep repo clean
- Update issue status immediately after merge
- Notify author of successful merge
