---
name: op-identify-current-gate
description: Identify the current quality gate by checking PR labels
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Identify Current Gate


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Gate Label Mapping](#gate-label-mapping)
- [Steps](#steps)
  - [Step 1: Get PR Labels](#step-1-get-pr-labels)
  - [Step 2: Filter Gate Labels](#step-2-filter-gate-labels)
  - [Step 3: Determine Current Gate](#step-3-determine-current-gate)
  - [Step 4: Determine Gate Status](#step-4-determine-gate-status)
  - [Step 5: Return Gate Information](#step-5-return-gate-information)
- [Gate Progression Flow](#gate-progression-flow)
- [Example](#example)
- [Decision Logic Script](#decision-logic-script)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Determine which quality gate a PR is currently at by examining its labels. This is the first step in quality gate enforcement.

## When to Use

- At the start of any gate enforcement workflow
- When resuming gate processing after interruption
- To determine next actions for a PR

## Prerequisites

- PR exists and is open
- GitHub CLI authenticated
- Access to repository labels

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to check |
| repo | string | No | Repository in owner/repo format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| current_gate | string | pre-review, review, pre-merge, post-merge, or none |
| gate_status | string | pending, passed, failed, or unknown |
| labels | array | All gate-related labels on the PR |

## Gate Label Mapping

| Label Pattern | Gate | Status |
|---------------|------|--------|
| No gate labels | Pre-Review | Pending (default) |
| `gate:pre-review-pending` | Pre-Review | Pending |
| `gate:pre-review-passed` | Pre-Review | Passed |
| `gate:pre-review-failed` | Pre-Review | Failed |
| `gate:review-pending` | Review | Pending |
| `gate:review-passed` | Review | Passed |
| `gate:review-failed` | Review | Failed |
| `gate:pre-merge-pending` | Pre-Merge | Pending |
| `gate:pre-merge-passed` | Pre-Merge | Passed |
| `gate:pre-merge-failed` | Pre-Merge | Failed |
| `gate:post-merge-passed` | Post-Merge | Passed |
| `gate:post-merge-failed` | Post-Merge | Failed |

## Steps

### Step 1: Get PR Labels

```bash
gh pr view <NUMBER> --json labels --jq '.labels[].name'
```

### Step 2: Filter Gate Labels

Look for labels matching pattern `gate:*`:

```bash
gh pr view <NUMBER> --json labels --jq '.labels[].name | select(startswith("gate:"))'
```

### Step 3: Determine Current Gate

Parse the highest-progress gate label:
1. If post-merge label exists -> Post-Merge Gate
2. If pre-merge label exists -> Pre-Merge Gate
3. If review label exists -> Review Gate
4. If pre-review label exists -> Pre-Review Gate
5. If no gate labels -> Pre-Review Gate (default)

### Step 4: Determine Gate Status

From the label suffix:
- `-pending` -> Pending
- `-passed` -> Passed (proceed to next gate)
- `-failed` -> Failed (requires action)

### Step 5: Return Gate Information

```json
{
  "pr_number": 123,
  "current_gate": "review",
  "gate_status": "pending",
  "labels": ["gate:pre-review-passed", "gate:review-pending"],
  "next_action": "execute_review_gate_checks"
}
```

## Gate Progression Flow

```
PR Created
    ↓
Pre-Review Gate (pending)
    ↓ [pass]
Review Gate (pending)
    ↓ [pass]
Pre-Merge Gate (pending)
    ↓ [pass]
MERGE
    ↓
Post-Merge Gate
```

## Example

```bash
# Get all labels
gh pr view 123 --json labels --jq '.labels[].name'
# Output:
# enhancement
# gate:pre-review-passed
# gate:review-pending

# Interpretation:
# - Pre-Review Gate: PASSED
# - Review Gate: PENDING (current)
# - Current action: Execute Review Gate checks
```

## Decision Logic Script

```bash
#!/bin/bash
PR_NUMBER=$1

# Get gate labels
LABELS=$(gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("gate:"))')

# Determine current gate (check in reverse order)
if echo "$LABELS" | grep -q "gate:post-merge"; then
    CURRENT_GATE="post-merge"
elif echo "$LABELS" | grep -q "gate:pre-merge"; then
    CURRENT_GATE="pre-merge"
elif echo "$LABELS" | grep -q "gate:review"; then
    CURRENT_GATE="review"
else
    CURRENT_GATE="pre-review"
fi

# Determine status
if echo "$LABELS" | grep -q "gate:${CURRENT_GATE}-passed"; then
    STATUS="passed"
elif echo "$LABELS" | grep -q "gate:${CURRENT_GATE}-failed"; then
    STATUS="failed"
else
    STATUS="pending"
fi

echo "Current Gate: $CURRENT_GATE"
echo "Status: $STATUS"
```

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | Return error, verify PR number |
| Conflicting labels | Flag inconsistency, use highest gate |
| No labels access | Check permissions |

## Related Operations

- [op-execute-pre-review-gate.md](op-execute-pre-review-gate.md) - If at Pre-Review
- [op-execute-review-gate.md](op-execute-review-gate.md) - If at Review
- [op-execute-pre-merge-gate.md](op-execute-pre-merge-gate.md) - If at Pre-Merge
- [op-execute-post-merge-gate.md](op-execute-post-merge-gate.md) - If at Post-Merge
