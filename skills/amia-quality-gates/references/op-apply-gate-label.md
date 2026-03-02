---
name: op-apply-gate-label
description: Apply appropriate gate status label to PR
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Apply Gate Label


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Label Format](#label-format)
- [Warning Labels](#warning-labels)
- [Steps](#steps)
  - [Step 1: Remove Previous Status Labels for Same Gate](#step-1-remove-previous-status-labels-for-same-gate)
  - [Step 2: Add New Status Label](#step-2-add-new-status-label)
  - [Step 3: Add Warning Labels (If Applicable)](#step-3-add-warning-labels-if-applicable)
  - [Step 4: Verify Labels Applied](#step-4-verify-labels-applied)
- [Label Application Rules](#label-application-rules)
- [Example: Gate Passed](#example-gate-passed)
- [Example: Gate Failed with Warnings](#example-gate-failed-with-warnings)
- [Label Creation](#label-creation)
- [Batch Label Script](#batch-label-script)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Apply the correct gate status label to a PR based on gate evaluation results. Labels communicate gate status to all stakeholders.

## When to Use

- After any gate evaluation completes
- When gate status changes
- To update PR state visibility

## Prerequisites

- Gate evaluation completed
- Gate decision determined (passed/failed)
- Permission to modify PR labels

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| gate | string | Yes | pre-review, review, pre-merge, or post-merge |
| status | string | Yes | pending, passed, or failed |
| warnings | array | No | Warning labels to add |

## Output

| Field | Type | Description |
|-------|------|-------------|
| labels_added | array | Labels that were added |
| labels_removed | array | Labels that were removed |
| current_labels | array | All labels now on PR |

## Label Format

Gate labels follow the pattern: `gate:<gate-name>-<status>`

| Gate | Pending | Passed | Failed |
|------|---------|--------|--------|
| Pre-Review | `gate:pre-review-pending` | `gate:pre-review-passed` | `gate:pre-review-failed` |
| Review | `gate:review-pending` | `gate:review-passed` | `gate:review-failed` |
| Pre-Merge | `gate:pre-merge-pending` | `gate:pre-merge-passed` | `gate:pre-merge-failed` |
| Post-Merge | N/A | `gate:post-merge-passed` | `gate:post-merge-failed` |

## Warning Labels

| Label | When Applied |
|-------|--------------|
| `gate:low-coverage` | Test coverage below threshold |
| `gate:missing-changelog` | No changelog entry |
| `gate:large-pr` | PR exceeds size threshold |
| `gate:style-issues` | Style/formatting issues |
| `gate:performance-concern` | Performance warnings |
| `gate:flaky-test` | Flaky test detected |
| `gate:override-applied` | Gate override was used |

## Steps

### Step 1: Remove Previous Status Labels for Same Gate

```bash
# Remove all status variants for the gate
gh pr edit <NUMBER> \
    --remove-label "gate:<GATE>-pending" \
    --remove-label "gate:<GATE>-passed" \
    --remove-label "gate:<GATE>-failed"
```

### Step 2: Add New Status Label

```bash
gh pr edit <NUMBER> --add-label "gate:<GATE>-<STATUS>"
```

### Step 3: Add Warning Labels (If Applicable)

```bash
# Add any warning labels
gh pr edit <NUMBER> --add-label "gate:low-coverage"
```

### Step 4: Verify Labels Applied

```bash
gh pr view <NUMBER> --json labels --jq '.labels[].name'
```

## Label Application Rules

1. **Only one status per gate**: Remove other statuses before adding new one
2. **Preserve other gate labels**: Don't remove labels from other gates
3. **Warning labels accumulate**: Don't remove warnings automatically
4. **Override label is permanent**: Once applied, keep until merge

## Example: Gate Passed

```bash
# Pre-Review gate passed
gh pr edit 123 \
    --remove-label "gate:pre-review-pending" \
    --remove-label "gate:pre-review-failed" \
    --add-label "gate:pre-review-passed" \
    --add-label "gate:review-pending"

# Verify
gh pr view 123 --json labels --jq '.labels[].name | select(startswith("gate:"))'
# Output:
# gate:pre-review-passed
# gate:review-pending
```

## Example: Gate Failed with Warnings

```bash
# Review gate failed with warnings
gh pr edit 123 \
    --remove-label "gate:review-pending" \
    --add-label "gate:review-failed" \
    --add-label "gate:low-coverage" \
    --add-label "gate:style-issues"
```

## Label Creation

If label doesn't exist in repository, create it first:

```bash
# Create gate labels with appropriate colors
gh label create "gate:pre-review-pending" --color "FEF2C0" --description "Pre-review gate pending"
gh label create "gate:pre-review-passed" --color "0E8A16" --description "Pre-review gate passed"
gh label create "gate:pre-review-failed" --color "D73A49" --description "Pre-review gate failed"

# Colors:
# Pending: FEF2C0 (yellow)
# Passed: 0E8A16 (green)
# Failed: D73A49 (red)
# Warning: FBCA04 (orange)
```

## Batch Label Script

```bash
#!/bin/bash
PR_NUMBER=$1
GATE=$2
STATUS=$3

# Remove existing status labels for this gate
for S in pending passed failed; do
    gh pr edit $PR_NUMBER --remove-label "gate:${GATE}-${S}" 2>/dev/null || true
done

# Add new status label
gh pr edit $PR_NUMBER --add-label "gate:${GATE}-${STATUS}"

# If passed and not post-merge, add next gate pending
case "$GATE-$STATUS" in
    "pre-review-passed")
        gh pr edit $PR_NUMBER --add-label "gate:review-pending"
        ;;
    "review-passed")
        gh pr edit $PR_NUMBER --add-label "gate:pre-merge-pending"
        ;;
esac

echo "Labels updated for PR #$PR_NUMBER: gate:${GATE}-${STATUS}"
```

## Error Handling

| Error | Action |
|-------|--------|
| Label doesn't exist | Create label first using gh label create |
| No permission | Check collaborator status, escalate |
| Rate limit | Retry with backoff |

## Related Operations

- [op-identify-current-gate.md](op-identify-current-gate.md) - Reads gate labels
- [label-reference.md](label-reference.md) - Complete label list
- All gate execution operations - Use this after evaluation
