---
name: op-start-pr-review
description: Operation procedure for starting a PR review by updating review labels.
workflow-instruction: "support"
procedure: "support-skill"
---

# Operation: Start PR Review


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify PR Exists and Status](#step-1-verify-pr-exists-and-status)
  - [Step 2: Check Priority and Type](#step-2-check-priority-and-type)
  - [Step 3: Update Review Label](#step-3-update-review-label)
  - [Step 4: Comment on PR (Optional)](#step-4-comment-on-pr-optional)
  - [Step 5: Verify Label Update](#step-5-verify-label-update)
- [Example](#example)
- [Review Depth by Type](#review-depth-by-type)
- [Error Handling](#error-handling)
- [Notes](#notes)

## Purpose

Mark a pull request as under active review by updating the review label from `review:needed` to `review:in-progress`.

## When to Use

- When beginning to review a PR
- When resuming a paused review
- When taking over a review from another reviewer

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- PR number to review
- PR is in `review:needed` state

## Procedure

### Step 1: Verify PR Exists and Status

```bash
gh pr view $PR_NUMBER --json number,title,state,labels
```

Confirm PR is open and has `review:needed` label.

### Step 2: Check Priority and Type

```bash
# Check priority for review urgency
PRIORITY=$(gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("priority:"))')
echo "Priority: $PRIORITY"

# Check type for review depth
TYPE=$(gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("type:"))')
echo "Type: $TYPE"
```

### Step 3: Update Review Label

```bash
gh pr edit $PR_NUMBER --remove-label "review:needed" --add-label "review:in-progress"
```

### Step 4: Comment on PR (Optional)

```bash
gh pr comment $PR_NUMBER --body "Starting review. Priority: $PRIORITY, Type: $TYPE."
```

### Step 5: Verify Label Update

```bash
gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("review:"))'
# Expected: review:in-progress
```

## Example

**Scenario:** Start reviewing PR #45 which is labeled `review:needed`, `priority:high`.

```bash
# Step 1: Check PR status
gh pr view 45 --json title,state,labels
# Confirm: state=open, has review:needed

# Step 2: Update label
gh pr edit 45 --remove-label "review:needed" --add-label "review:in-progress"

# Step 3: Comment
gh pr comment 45 --body "Starting review. Will prioritize due to high priority label."

# Step 4: Verify
gh pr view 45 --json labels --jq '.labels[].name'
# Output includes: review:in-progress
```

## Review Depth by Type

| Type Label | Review Depth |
|------------|--------------|
| `type:security` | Deep security audit |
| `type:refactor` | Focus on behavior preservation |
| `type:docs` | Light review |
| `type:feature` | Full functionality review |
| `type:bug` | Focus on fix correctness |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Label not found | `review:needed` not present | Check if already in review |
| Permission denied | No write access to PR | Verify GitHub token scopes |
| PR not found | Invalid PR number | Verify with `gh pr list` |
| PR closed | Already merged or closed | Skip review, update status |

## Notes

- Only one reviewer should mark in-progress at a time
- If taking over, coordinate with previous reviewer
- High priority PRs should be started immediately
