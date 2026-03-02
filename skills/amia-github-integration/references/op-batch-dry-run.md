---
name: op-batch-dry-run
description: "Preview batch operations before executing them"
procedure: support-skill
workflow-instruction: support
---

# Operation: Batch Dry Run


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Build the filter query](#step-1-build-the-filter-query)
  - [Step 2: Preview target issues](#step-2-preview-target-issues)
  - [Step 3: Count affected issues](#step-3-count-affected-issues)
  - [Step 4: Preview specific changes](#step-4-preview-specific-changes)
  - [Step 5: Generate dry-run report](#step-5-generate-dry-run-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Dry-Run Patterns](#dry-run-patterns)
  - [Label addition dry-run](#label-addition-dry-run)
  - [Close operation dry-run](#close-operation-dry-run)
  - [Bulk assignee dry-run](#bulk-assignee-dry-run)
- [Error Handling](#error-handling)
  - [Empty result set](#empty-result-set)
  - [Permission preview mismatch](#permission-preview-mismatch)
- [Verification](#verification)

## Purpose

Preview the effects of a batch operation without making any changes. Essential for validating batch commands before execution.

## When to Use

- Before any destructive or bulk modification operation
- When testing new batch operation patterns
- When auditing what changes would be made
- Before closing or labeling many issues

## Prerequisites

1. GitHub CLI authenticated (`gh auth status`)
2. Read access to repository issues

## Procedure

### Step 1: Build the filter query

First, construct the filter that selects target issues:

```bash
# Define your filter criteria
FILTER_CMD="gh issue list --label \"stale\" --state open"
```

### Step 2: Preview target issues

Display the issues that would be affected:

```bash
# Show issue numbers and titles
$FILTER_CMD --json number,title --jq '.[] | "Issue #\(.number): \(.title)"'
```

### Step 3: Count affected issues

```bash
# Get total count
$FILTER_CMD --json number | jq 'length'
```

### Step 4: Preview specific changes

For label operations:
```bash
# Show current labels vs proposed labels
$FILTER_CMD --json number,title,labels --jq '.[] | {number, title, current_labels: [.labels[].name], will_add: ["new-label"]}'
```

For state changes:
```bash
# Show which issues would be closed
$FILTER_CMD --json number,title,state --jq '.[] | "Would close #\(.number): \(.title)"'
```

### Step 5: Generate dry-run report

```bash
# Full dry-run report
echo "=== DRY RUN REPORT ==="
echo "Operation: Add label 'reviewed'"
echo "Target filter: --label stale --state open"
echo ""
echo "Issues that would be affected:"
$FILTER_CMD --json number,title --jq '.[] | "#\(.number) - \(.title)"'
echo ""
echo "Total issues: $($FILTER_CMD --json number | jq 'length')"
echo ""
echo "To execute: Remove --dry-run flag or confirm below"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| operation | string | yes | Type of operation (add-label, remove-label, close, etc.) |
| filter | object | yes | Filter criteria for target selection |
| changes | object | yes | Changes that would be applied |

## Output

| Field | Type | Description |
|-------|------|-------------|
| would_affect | number | Count of items that would be modified |
| items | object[] | List of items with current and proposed state |
| operation | string | Description of operation |
| warnings | string[] | Any potential issues detected |

## Example Output

```json
{
  "would_affect": 8,
  "items": [
    {
      "number": 12,
      "title": "Fix login bug",
      "current_labels": ["bug"],
      "proposed_labels": ["bug", "priority:high"]
    },
    {
      "number": 15,
      "title": "Update docs",
      "current_labels": ["documentation"],
      "proposed_labels": ["documentation", "priority:high"]
    }
  ],
  "operation": "add-label: priority:high",
  "warnings": []
}
```

## Dry-Run Patterns

### Label addition dry-run

```bash
gh issue list --label "bug" --state open --json number,title,labels | \
  jq '.[] | {
    number,
    title,
    current: [.labels[].name],
    after_add: ([.labels[].name] + ["new-label"] | unique)
  }'
```

### Close operation dry-run

```bash
gh issue list --label "stale" --state open --json number,title,updatedAt | \
  jq '.[] | "Would close: #\(.number) \(.title) (last update: \(.updatedAt))"'
```

### Bulk assignee dry-run

```bash
gh issue list --label "backlog" --state open --json number,title,assignees | \
  jq '.[] | {
    number,
    title,
    current_assignees: [.assignees[].login],
    would_assign: "triage-team"
  }'
```

## Error Handling

### Empty result set

**Cause**: No issues match the filter criteria.

**Solution**: This is informational - no issues would be affected. Verify filter is correct.

### Permission preview mismatch

**Cause**: Dry-run shows issues user cannot actually modify.

**Solution**: Filter results by permission level or verify write access.

## Verification

Always run dry-run before executing:

```bash
# Step 1: Dry run
DRY_RUN_COUNT=$(gh issue list --label "stale" --json number | jq 'length')
echo "Dry run: $DRY_RUN_COUNT issues would be affected"

# Step 2: Confirm with user before proceeding
# Step 3: Execute actual operation only after confirmation
```
