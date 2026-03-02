---
name: op-merge-decision
description: Execute merge or reject decision based on review results
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Merge Decision Execution


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Decision Matrix](#decision-matrix)
- [Steps](#steps)
  - [For APPROVED Decision (>= 80%)](#for-approved-decision-80)
- [Review Approved](#review-approved)
  - [For CHANGES_REQUESTED Decision (60-79%)](#for-changes_requested-decision-60-79)
- [Changes Requested](#changes-requested)
  - [Required Changes](#required-changes)
  - [Issues Found](#issues-found)
  - [For REJECTED Decision (< 60%)](#for-rejected-decision-60)
- [Review Rejected](#review-rejected)
  - [Critical Issues](#critical-issues)
  - [Recommended Action](#recommended-action)
- [Post-Decision Actions](#post-decision-actions)
  - [Notify Stakeholders](#notify-stakeholders)
  - [Update Related Issues](#update-related-issues)
- [Example](#example)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Execute the final merge or rejection decision based on the review results, applying appropriate labels and communicating the outcome.

## When to Use

- After review report is generated
- When confidence score and decision are finalized
- To complete the PR review workflow

## Prerequisites

- Review report completed
- Confidence score calculated (>= 80% for approval)
- All quality gates passed (if applicable)
- Reviewer has merge permissions

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| decision | string | Yes | APPROVED, CHANGES_REQUESTED, or REJECTED |
| confidence_score | float | Yes | Final confidence score |
| review_report_path | string | Yes | Path to the review report |
| findings | array | No | List of issues if not approved |

## Output

| Field | Type | Description |
|-------|------|-------------|
| action_taken | string | merged, rejected, or changes_requested |
| pr_state | string | New state of the PR |
| labels_applied | array | Labels added to the PR |
| notification_sent | boolean | Whether stakeholders were notified |

## Decision Matrix

| Score | Decision | Action |
|-------|----------|--------|
| >= 80% | APPROVED | Merge PR |
| 60-79% | CHANGES_REQUESTED | Request specific changes |
| < 60% | REJECTED | Close PR with explanation |

## Steps

### For APPROVED Decision (>= 80%)

#### Step 1: Apply Approval Label

```bash
gh pr edit <NUMBER> --add-label "review:approved"
```

#### Step 2: Add Review Comment

```bash
gh pr review <NUMBER> --approve --body "$(cat <<'EOF'
## Review Approved

**Confidence Score**: XX%

This PR has passed the two-stage review process and is approved for merge.

See full review report: <REPORT_PATH>
EOF
)"
```

#### Step 3: Merge the PR

```bash
# Squash merge (preferred)
gh pr merge <NUMBER> --squash --auto

# Or standard merge
gh pr merge <NUMBER> --merge
```

#### Step 4: Verify Merge Success

```bash
gh pr view <NUMBER> --json state,mergedAt
```

### For CHANGES_REQUESTED Decision (60-79%)

#### Step 1: Apply Changes Requested Label

```bash
gh pr edit <NUMBER> --add-label "review:changes-requested"
```

#### Step 2: Add Review Comment with Required Changes

```bash
gh pr review <NUMBER> --request-changes --body "$(cat <<'EOF'
## Changes Requested

**Confidence Score**: XX%

This PR requires the following changes before approval:

### Required Changes
1. <CHANGE_1>
2. <CHANGE_2>
3. <CHANGE_3>

### Issues Found
<LIST_OF_ISSUES>

Please address these issues and request a re-review.

See full review report: <REPORT_PATH>
EOF
)"
```

#### Step 3: Assign Back to Author

```bash
gh pr edit <NUMBER> --add-assignee <AUTHOR_USERNAME>
```

### For REJECTED Decision (< 60%)

#### Step 1: Apply Rejected Label

```bash
gh pr edit <NUMBER> --add-label "review:rejected"
```

#### Step 2: Add Rejection Comment

```bash
gh pr comment <NUMBER> --body "$(cat <<'EOF'
## Review Rejected

**Confidence Score**: XX%

This PR has been rejected due to significant issues that require major rework.

### Critical Issues
<LIST_OF_CRITICAL_ISSUES>

### Recommended Action
<SPECIFIC_RECOMMENDATIONS>

The author should:
1. Address all critical issues
2. Consider creating a new PR with the fixes
3. Request a fresh review

See full review report: <REPORT_PATH>
EOF
)"
```

#### Step 3: Close the PR

```bash
gh pr close <NUMBER>
```

## Post-Decision Actions

### Notify Stakeholders

Send a notification using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-eoa`
- **Subject**: `PR #<NUMBER> Review Complete: <DECISION>`
- **Priority**: `normal`
- **Content**: `{"type": "review-complete", "message": "PR #<NUMBER> review completed. Decision: <DECISION>. Confidence: XX%. Report: <PATH>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Update Related Issues

If PR is merged, update linked issues (see [op-close-related-issues.md](op-close-related-issues.md)).

## Example

```bash
# For an approved PR
gh pr edit 123 --add-label "review:approved"
gh pr review 123 --approve --body "Review approved with 85% confidence."
gh pr merge 123 --squash --auto

# For changes requested
gh pr edit 123 --add-label "review:changes-requested"
gh pr review 123 --request-changes --body "Please fix security issues found."

# For rejected PR
gh pr edit 123 --add-label "review:rejected"
gh pr comment 123 --body "PR rejected due to critical issues."
gh pr close 123
```

## Error Handling

| Error | Action |
|-------|--------|
| Merge conflicts | Cannot merge - request conflict resolution |
| CI checks failing | Cannot merge - wait for CI or investigate failures |
| No merge permission | Escalate to authorized reviewer |
| PR already merged | Skip merge, proceed with post-merge actions |

## Related Operations

- [op-create-review-report.md](op-create-review-report.md) - Provides report input
- [op-close-related-issues.md](op-close-related-issues.md) - Post-merge issue closure
