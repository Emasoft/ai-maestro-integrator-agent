---
name: op-mark-blocked-pr
description: Operation procedure for marking a PR as blocked when it cannot be reviewed.
workflow-instruction: "support"
procedure: "support-skill"
---

# Operation: Mark Blocked PR


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify Blocker Type](#step-1-identify-blocker-type)
  - [Step 2: Add Blocked Label](#step-2-add-blocked-label)
  - [Step 3: Comment with Blocker Details](#step-3-comment-with-blocker-details)
  - [Step 4: Notify Author (if agent)](#step-4-notify-author-if-agent)
  - [Step 5: Verify Label Update](#step-5-verify-label-update)
- [Example](#example)
- [Blocker Templates](#blocker-templates)
  - [Merge Conflicts](#merge-conflicts)
- [Review Blocked: Merge Conflicts](#review-blocked-merge-conflicts)
  - [CI Failing](#ci-failing)
- [Review Blocked: CI Failures](#review-blocked-ci-failures)
  - [Dependent PR](#dependent-pr)
- [Review Blocked: Dependency](#review-blocked-dependency)
- [Unblocking a PR](#unblocking-a-pr)
- [Error Handling](#error-handling)
- [Notes](#notes)

## Purpose

Mark a PR as blocked when review cannot proceed due to merge conflicts, CI failures, missing dependencies, or other blockers.

## When to Use

- When PR has merge conflicts
- When CI checks are failing
- When dependent PRs must merge first
- When missing context/documentation to review
- When author is unresponsive

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- PR number to mark
- Blocker reason identified

## Procedure

### Step 1: Identify Blocker Type

| Blocker | Label to Add | Action Required |
|---------|--------------|-----------------|
| Merge conflicts | `review:blocked` | Author must rebase |
| CI failing | `review:blocked` | Author must fix CI |
| Dependent PR | `review:blocked` | Wait for dependency |
| Missing info | `review:blocked` | Author must clarify |
| Author unresponsive | `status:blocked` | Escalate to AMCOS |

### Step 2: Add Blocked Label

```bash
gh pr edit $PR_NUMBER --add-label "review:blocked"
# Keep in-progress if just waiting
# Or remove if cannot proceed
gh pr edit $PR_NUMBER --remove-label "review:in-progress"
```

### Step 3: Comment with Blocker Details

```bash
gh pr comment $PR_NUMBER --body "## Review Blocked

**Reason:** $BLOCKER_REASON

**Action Required:**
$REQUIRED_ACTION

**Blocked at:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

Please address the blocker and comment when ready for re-review."
```

### Step 4: Notify Author (if agent)

Get the PR author:
```bash
AUTHOR=$(gh pr view $PR_NUMBER --json author --jq '.author.login')
```

Then send a message using the `agent-messaging` skill with:
- **Recipient**: The PR author agent
- **Subject**: `PR #<PR_NUMBER> blocked`
- **Priority**: `high`
- **Content**: `{"type": "review-blocked", "message": "Your PR is blocked: <BLOCKER_REASON>. Please address and notify when ready.", "pr_number": <PR_NUMBER>}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Step 5: Verify Label Update

```bash
gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("review:"))'
# Expected: review:blocked
```

## Example

**Scenario:** PR #45 has merge conflicts with main branch.

```bash
# Step 1: Add blocked label
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:blocked"

# Step 2: Comment
gh pr comment 45 --body "## Review Blocked

**Reason:** Merge conflicts detected with main branch

**Action Required:**
Please rebase your branch on latest main:
\`\`\`bash
git fetch origin
git rebase origin/main
git push --force-with-lease
\`\`\`

**Blocked at:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

Please resolve conflicts and comment when ready for re-review."

# Step 3: Verify
gh pr view 45 --json labels --jq '.labels[].name'
# Output includes: review:blocked
```

## Blocker Templates

### Merge Conflicts

```markdown
## Review Blocked: Merge Conflicts

Your branch has conflicts with main. Please rebase:
```bash
git fetch origin
git rebase origin/main
# resolve conflicts
git push --force-with-lease
```

Comment when resolved.
```

### CI Failing

```markdown
## Review Blocked: CI Failures

The following checks are failing:
- test-suite: 3 failures
- lint: 2 errors

Please fix and push. Comment when CI is green.
```

### Dependent PR

```markdown
## Review Blocked: Dependency

This PR depends on #$OTHER_PR which must merge first.

Will resume review once dependency is merged.
```

## Unblocking a PR

When blocker is resolved:

```bash
# Remove blocked label
gh pr edit $PR_NUMBER --remove-label "review:blocked"

# Return to in-progress or needed
gh pr edit $PR_NUMBER --add-label "review:in-progress"

# Comment
gh pr comment $PR_NUMBER --body "Blocker resolved. Resuming review."
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Label not found | `review:blocked` doesn't exist | Create with `gh label create` |
| Author not found | PR author not an agent | Leave detailed PR comment |
| Multiple blockers | Several issues | List all in comment |

## Notes

- Document blocker clearly with required action
- Set reasonable expectations for resolution
- Escalate to AMCOS if author unresponsive for >24h
- Track blocked PRs for daily standup reporting
