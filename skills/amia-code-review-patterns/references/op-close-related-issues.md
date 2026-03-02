---
name: op-close-related-issues
description: Close GitHub issues linked to a merged PR
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Close Related Issues


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Get PR Details and Linked Issues](#step-1-get-pr-details-and-linked-issues)
  - [Step 2: Parse Linked Issues](#step-2-parse-linked-issues)
  - [Step 3: Verify Each Issue](#step-3-verify-each-issue)
  - [Step 4: Close Open Issues](#step-4-close-open-issues)
  - [Step 5: Document Closures](#step-5-document-closures)
- [Automatic Closure Behavior](#automatic-closure-behavior)
- [Example](#example)
- [Complete Script](#complete-script)
- [Verification Checklist](#verification-checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

After a PR is merged, close all issues that were linked to and resolved by the PR.

## When to Use

- After a PR has been successfully merged
- When issues are linked with "closes #", "fixes #", or "resolves #"
- As the final step of the PR integration workflow

## Prerequisites

- PR is merged (not just approved)
- Issues are properly linked in PR description
- Agent has permission to close issues

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The merged PR number |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| closed_issues | array | List of issue numbers that were closed |
| already_closed | array | Issues that were already closed |
| failed_to_close | array | Issues that could not be closed (with reasons) |

## Steps

### Step 1: Get PR Details and Linked Issues

```bash
# Get PR body to find linked issues
gh pr view <NUMBER> --json body,closingIssuesReferences
```

### Step 2: Parse Linked Issues

Look for patterns in PR body:
- `closes #123`
- `fixes #123`
- `resolves #123`
- `close #123`
- `fix #123`
- `resolve #123`

Also check GitHub's automatic linking:
```bash
gh pr view <NUMBER> --json closingIssuesReferences --jq '.closingIssuesReferences[].number'
```

### Step 3: Verify Each Issue

For each linked issue:
```bash
gh issue view <ISSUE_NUMBER> --json state,title
```

### Step 4: Close Open Issues

For issues that are still open:
```bash
gh issue close <ISSUE_NUMBER> --comment "Closed by PR #<PR_NUMBER>"
```

### Step 5: Document Closures

Record which issues were closed for the report.

## Automatic Closure Behavior

GitHub automatically closes issues when:
1. PR body contains "closes #X", "fixes #X", or "resolves #X"
2. PR is merged to the default branch

**However**, you should verify closure because:
- Automatic closure may fail if syntax is incorrect
- PR may merge to non-default branch
- Issue may be in a different repository

## Example

```bash
# Get linked issues
gh pr view 123 --json closingIssuesReferences --jq '.closingIssuesReferences[].number'
# Output: 45
#         67

# Verify issue state
gh issue view 45 --json state
# Output: {"state":"CLOSED"}

gh issue view 67 --json state
# Output: {"state":"OPEN"}

# Close remaining open issue
gh issue close 67 --comment "Closed by PR #123"
```

## Complete Script

```bash
#!/bin/bash
PR_NUMBER=$1
REPO=${2:-""}

# Get linked issues
if [ -n "$REPO" ]; then
    ISSUES=$(gh pr view $PR_NUMBER --repo $REPO --json closingIssuesReferences --jq '.closingIssuesReferences[].number')
else
    ISSUES=$(gh pr view $PR_NUMBER --json closingIssuesReferences --jq '.closingIssuesReferences[].number')
fi

# Close each open issue
for ISSUE in $ISSUES; do
    STATE=$(gh issue view $ISSUE --json state --jq '.state')
    if [ "$STATE" = "OPEN" ]; then
        gh issue close $ISSUE --comment "Closed by PR #$PR_NUMBER"
        echo "Closed issue #$ISSUE"
    else
        echo "Issue #$ISSUE already closed"
    fi
done
```

## Verification Checklist

After closing issues, verify:
- [ ] All linked issues are now closed
- [ ] Closure comments reference the PR
- [ ] No issues were incorrectly closed
- [ ] Milestone progress updated (if applicable)

## Error Handling

| Error | Action |
|-------|--------|
| Issue not found | May be in different repo - check cross-repo links |
| No permission to close | Escalate to maintainer |
| Issue already closed | Log as already_closed, continue |
| Invalid issue reference | Log warning, skip |

## Related Operations

- [op-merge-decision.md](op-merge-decision.md) - Triggers this operation
- Post-merge verification workflow
